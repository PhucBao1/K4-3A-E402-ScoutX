"""Bonus "NÂNG CAO" của đề C3: dựng video hoàn chỉnh từ chính kịch bản agent vừa viết
(không bắt buộc, không ảnh hưởng điểm tiêu chí chính — xem tracks/track-c3.md).

Không phải dựng có animation/đồ hoạ đẹp — mục tiêu là chứng minh thật pipeline
"kịch bản -> video" chạy được: mỗi câu có "loi" được đọc thật bằng TTS, khung hình
tĩnh hiện đúng "chuTrenManHinh", ghép lại thành 1 file MP4 bằng ffmpeg.

Dùng: python3 render_video.py <đường_dẫn_kịch_bản.json> <đường_dẫn_output.mp4>
Kịch bản JSON phải đúng schema "hackathon-kich-ban/1" (field "kichBan" hoặc file
chỉ chứa thẳng object kichBan).
"""
import json
import os
import subprocess
import sys
import tempfile

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
client = OpenAI()

FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
WIDTH, HEIGHT = 1920, 1080
SILENCE_DEFAULT_SEC = 2.0


def tts_to_file(text: str, out_path: str) -> None:
    """Đọc thật 1 câu bằng OpenAI TTS — chi phí ước tính ghi trong README.md."""
    with client.audio.speech.with_streaming_response.create(
        model="tts-1", voice="alloy", input=text,
    ) as response:
        response.stream_to_file(out_path)


def make_silence(out_path: str, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(seconds), "-q:a", "9", out_path],
        check=True, capture_output=True,
    )


def audio_duration_sec(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def make_frame_image(chu_tren_man_hinh: str, out_path: str) -> None:
    """Khung hình tĩnh tối giản — chỉ chữ hiện đúng theo mau-kich-ban.md, canh giữa,
    chừa vùng dưới cho phụ đề (đúng chuẩn khung hình 1920x1080 của khoá)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(20, 24, 38))
    draw = ImageDraw.Draw(img)
    text = chu_tren_man_hinh or ""
    font_size = 90
    font = ImageFont.truetype(FONT_PATH, font_size)
    while True:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        if w <= WIDTH - 200 or font_size <= 30:
            break
        font_size -= 6
        font = ImageFont.truetype(FONT_PATH, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((WIDTH - w) / 2, (HEIGHT - h) / 2 - 60), text, font=font, fill=(255, 255, 255))
    img.save(out_path)


def render(kich_ban: dict, out_mp4: str) -> None:
    cau_list = kich_ban.get("cau", [])
    with tempfile.TemporaryDirectory() as tmp:
        segment_paths = []
        for i, cau in enumerate(cau_list):
            n = cau.get("n", i)
            audio_path = os.path.join(tmp, f"a_{i:03d}.mp3")
            if cau.get("loi"):
                print(f"[TTS] câu {n}: {cau['loi'][:50]}...")
                tts_to_file(cau["loi"], audio_path)
                duration = audio_duration_sec(audio_path)
            else:
                duration = float(cau.get("dungGiay", SILENCE_DEFAULT_SEC))
                make_silence(audio_path, duration)

            image_path = os.path.join(tmp, f"i_{i:03d}.png")
            make_frame_image(cau.get("chuTrenManHinh", ""), image_path)

            segment_path = os.path.join(tmp, f"s_{i:03d}.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", image_path, "-i", audio_path,
                 "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
                 "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
                 "-t", str(duration), segment_path],
                check=True, capture_output=True,
            )
            segment_paths.append(segment_path)

        concat_list_path = os.path.join(tmp, "concat.txt")
        with open(concat_list_path, "w") as f:
            for p in segment_paths:
                f.write(f"file '{p}'\n")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
             "-c", "copy", out_mp4],
            check=True, capture_output=True,
        )
    print(f"Xong: {out_mp4}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Dùng: python3 render_video.py <kich_ban.json> <output.mp4>")
        sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    kich_ban = data.get("kichBan", data)
    render(kich_ban, sys.argv[2])
