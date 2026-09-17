"""Bonus "NÂNG CAO" của đề C3: dựng video hoàn chỉnh từ chính kịch bản agent vừa viết
(không bắt buộc, không ảnh hưởng điểm tiêu chí chính — xem tracks/track-c3.md).

Vẫn không phải animation thật (không chuyển động), nhưng mỗi cảnh có 1 ảnh minh hoạ
tĩnh do DALL-E vẽ theo đúng "yDoHinh" (rớt về khung chữ trắng trơn nếu vẽ lỗi), ghép
với "loi" đọc thật bằng TTS và "chuTrenManHinh" ở dải phụ đề, xuất ra 1 file MP4.

Dùng: python3 render_video.py <đường_dẫn_kịch_bản.json> <đường_dẫn_output.mp4>
Kịch bản JSON phải đúng schema "hackathon-kich-ban/1" (field "kichBan" hoặc file
chỉ chứa thẳng object kichBan).
"""
import base64
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


def draw_caption(img: Image.Image, chu_tren_man_hinh: str) -> None:
    """Vẽ "chuTrenManHinh" ở dải dưới cùng — tách riêng khỏi minh hoạ chính, đúng
    "vùng an toàn chừa cho phụ đề" trong mau-kich-ban.md."""
    draw = ImageDraw.Draw(img)
    text = chu_tren_man_hinh or ""
    if not text:
        return
    font_size = 54
    font = ImageFont.truetype(FONT_PATH, font_size)
    while True:
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= WIDTH - 160 or font_size <= 28:
            break
        font_size -= 4
        font = ImageFont.truetype(FONT_PATH, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    band_top = HEIGHT - 150
    draw.rectangle([0, band_top, WIDTH, HEIGHT], fill=(0, 0, 0))
    draw.text(((WIDTH - w) / 2, band_top + (150 - h) / 2 - 10), text, font=font, fill=(255, 255, 255))


def make_frame_image(chu_tren_man_hinh: str, out_path: str) -> None:
    """Khung hình tĩnh tối giản (fallback) — chỉ chữ hiện đúng theo mau-kich-ban.md, canh giữa,
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


def make_illustrated_frame(y_do_hinh: str, chu_tren_man_hinh: str, out_path: str) -> bool:
    """Bonus: vẽ 1 ảnh minh hoạ bằng DALL-E theo đúng "yDoHinh" thay vì chữ trắng trơn, rồi ghép
    "chuTrenManHinh" vào dải phụ đề dưới cùng. Trả về False (không raise) nếu vẽ lỗi — gọi nơi
    dùng phải tự rớt về make_frame_image(), không được để hỏng cả video vì 1 ảnh lỗi."""
    if not y_do_hinh:
        return False
    try:
        prompt = (
            f"Minh hoạ đơn giản, phong cách phẳng (flat illustration), màu sắc rõ ràng, không chữ, "
            f"không watermark, cho cảnh trong video bài giảng: {y_do_hinh}"
        )
        resp = client.images.generate(
            model="gpt-image-1", prompt=prompt, size="1536x1024", n=1,
        )
        img_bytes = base64.b64decode(resp.data[0].b64_json)
        tmp_raw = out_path + ".raw.png"
        with open(tmp_raw, "wb") as f:
            f.write(img_bytes)
        raw = Image.open(tmp_raw).convert("RGB")
        # Resize + crop giữa để lấp đúng 1920x1080 (DALL-E trả 1792x1024, không đúng tỉ lệ 16:9)
        scale = max(WIDTH / raw.width, HEIGHT / raw.height)
        raw = raw.resize((round(raw.width * scale), round(raw.height * scale)))
        left = (raw.width - WIDTH) // 2
        top = (raw.height - HEIGHT) // 2
        canvas = raw.crop((left, top, left + WIDTH, top + HEIGHT))
        draw_caption(canvas, chu_tren_man_hinh)
        canvas.save(out_path)
        os.remove(tmp_raw)
        return True
    except Exception as e:
        print(f"[DALL-E] Vẽ minh hoạ lỗi, dùng khung chữ tĩnh thay thế: {e}")
        return False


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
            ok = make_illustrated_frame(cau.get("yDoHinh", ""), cau.get("chuTrenManHinh", ""), image_path)
            if not ok:
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
