"""Thử nghiệm NÂNG CAO thứ 2 (tách biệt khỏi render_video.py đang chạy ổn định): dựng video
bằng HyperFrames (github.com/heygen-com/hyperframes) thay vì ảnh tĩnh — AI viết ra 1 scene
HTML/CSS/GSAP mỗi câu, HyperFrames render thành khung hình CHUYỂN ĐỘNG thật (kinetic text +
biểu đồ đơn giản), rồi ghép với audio TTS thật giống hệt render_video.py.

Không đụng vào render_video.py hiện có — đây là con đường thử nghiệm riêng, đúng như đã bàn:
"làm sau CP4, coi như thử nghiệm tách biệt, không đánh đổi rủi ro vào bản nộp chính".

Yêu cầu môi trường: Node.js >= 22 + `hyperframes` CLI + Chrome Headless Shell — đã cài SẴN,
CỐ ĐỊNH tại ~/.local/hyperframes-tools/ (không phải thư mục tạm, không mất khi hết phiên làm
việc). Cài đặt gốc: tải Node prebuilt từ nodejs.org (không cần sudo) → `npm install -g
hyperframes` với prefix trỏ vào ~/.local/hyperframes-tools/npm-global → `hyperframes browser
ensure` (Chrome Headless Shell tự lưu vào ~/.cache/hyperframes/, đã persistent sẵn).
Máy khác chưa có thì set biến môi trường HF_NODE_BIN_DIR / HF_BIN_DIR trỏ đúng chỗ cài, hoặc
cài lại đúng 3 bước trên vào đúng đường dẫn mặc định bên dưới.

Dùng: python3 render_video_hyperframes.py <đường_dẫn_kịch_bản.json> <đường_dẫn_output.mp4>
"""
import html
import json
import os
import subprocess
import sys
import tempfile

from render_video import audio_duration_sec, make_silence, tts_to_file
from render_video import client as openai_client
from prompt import HYPERFRAMES_SCENE_PROMPT

_HOME = os.path.expanduser("~")
_DEFAULT_NODE_BIN = os.path.join(_HOME, ".local/hyperframes-tools/node/bin")
_DEFAULT_HF_BIN = os.path.join(_HOME, ".local/hyperframes-tools/npm-global/bin")

# Mặc định trỏ vào chỗ đã cài cố định ở trên — override bằng biến môi trường nếu máy khác.
NODE_BIN_DIR = os.environ.get("HF_NODE_BIN_DIR") or (
    _DEFAULT_NODE_BIN if os.path.isdir(_DEFAULT_NODE_BIN) else ""
)
HYPERFRAMES_BIN_DIR = os.environ.get("HF_BIN_DIR") or (
    _DEFAULT_HF_BIN if os.path.isdir(_DEFAULT_HF_BIN) else ""
)

WIDTH, HEIGHT = 1920, 1080
SILENCE_DEFAULT_SEC = 2.0

SCENE_TEMPLATE = """<!doctype html>
<html lang="vi" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500..700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        width: 1920px; height: 1080px; overflow: hidden;
        background: #0A0A0F;
        font-family: 'IBM Plex Sans', Arial, sans-serif;
      }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      #eyebrow {{
        position: absolute; left: 128px; top: 96px;
        color: #58C4DD; font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 28px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase;
        opacity: 0;
      }}
      #headline {{
        position: absolute; left: 128px; top: 220px; width: 1600px;
        color: #F5F5F5; font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 76px; font-weight: 700; line-height: 1.15;
        opacity: 0;
      }}
      #accent-bar {{
        position: absolute; left: 128px; top: 176px; width: 120px; height: 8px;
        background: #58C4DD; border-radius: 4px; transform: scaleX(0); transform-origin: left;
      }}
      #caption {{
        position: absolute; left: 128px; bottom: 120px; width: 1664px;
        color: #B7B7C2; font-size: 34px; line-height: 1.5;
        opacity: 0;
      }}
      #source-tag {{
        position: absolute; right: 128px; top: 96px;
        color: #B7B7C2; font-size: 22px;
        background: #16161F; padding: 10px 20px; border-radius: 100px;
        opacity: 0;
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      class="clip"
      data-composition-id="main"
      data-start="0"
      data-duration="{duration}"
      data-width="1920"
      data-height="1080"
    >
      <p id="eyebrow" class="clip" data-start="0" data-duration="{duration}" data-track-index="0">{eyebrow}</p>
      <div id="accent-bar" class="clip" data-start="0" data-duration="{duration}" data-track-index="1"></div>
      <h1 id="headline" class="clip" data-start="0" data-duration="{duration}" data-track-index="2">{headline}</h1>
      <p id="caption" class="clip" data-start="0" data-duration="{duration}" data-track-index="3">{caption}</p>
      {source_tag_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.to("#eyebrow", {{ opacity: 1, duration: 0.4 }}, 0.1);
      tl.to("#accent-bar", {{ scaleX: 1, duration: 0.5 }}, 0.3);
      tl.fromTo("#headline", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.6 }}, 0.4);
      tl.fromTo("#caption", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, 1.0);
      tl.to("#source-tag", {{ opacity: 1, duration: 0.4 }}, 1.2);
      tl.to("#root", {{ opacity: 0, duration: 0.35 }}, {fade_out_start});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


def _bin_path(name: str) -> str:
    for d in (HYPERFRAMES_BIN_DIR, NODE_BIN_DIR):
        if d:
            candidate = os.path.join(d, name)
            if os.path.exists(candidate):
                return candidate
    return name  # trông cậy vào PATH hệ thống


def _run_env() -> dict:
    env = dict(os.environ)
    extra = [d for d in (HYPERFRAMES_BIN_DIR, NODE_BIN_DIR) if d]
    if extra:
        env["PATH"] = ":".join(extra) + ":" + env.get("PATH", "")
    return env


def render_scene_html(cau: dict, duration: float) -> str:
    headline = html.escape(cau.get("chuTrenManHinh") or cau.get("loi", "")[:40])
    caption = html.escape(cau.get("loi", ""))
    eyebrow = "ScriptScout"
    source_tag_html = ""
    goi_y = cau.get("goiYHienNguon")
    if goi_y:
        source_tag_html = (
            f'<p id="source-tag" class="clip" data-start="0" data-duration="{duration}" '
            f'data-track-index="4">{html.escape(goi_y)}</p>'
        )
    fade_out_start = max(duration - 0.4, 0.1)
    return SCENE_TEMPLATE.format(
        duration=duration, headline=headline, caption=caption, eyebrow=eyebrow,
        source_tag_html=source_tag_html, fade_out_start=fade_out_start,
    )


AI_SCENE_WRAPPER = """<!doctype html>
<html lang="vi" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500..700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        width: 1920px; height: 1080px; overflow: hidden;
        background: #0A0A0F;
        font-family: 'IBM Plex Sans', Arial, sans-serif;
      }}
      #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div
      id="root"
      class="clip"
      data-composition-id="main"
      data-start="0"
      data-duration="{duration}"
      data-width="1920"
      data-height="1080"
    >
      {ai_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {ai_gsap}
      tl.to("#root", {{ opacity: 0, duration: 0.35 }}, {fade_out_start});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


def generate_ai_scene(cau: dict, duration: float) -> dict | None:
    """Cho AI tự thiết kế bố cục cảnh (đa dạng hơn 1 template cố định), guard chặt: bắt buộc
    chữ tiêu đề + lời đọc phải xuất hiện NGUYÊN VĂN trong HTML trả về, không cho paraphrase/bịa
    thêm chữ — đúng nguyên tắc "chữ trên màn hình không được lệch nội dung" đã áp dụng cho
    validate_output() ở main.py. Trả về None nếu AI lỗi/vi phạm, để nơi gọi tự rớt về
    render_scene_html() (bản mẫu cố định, an toàn tuyệt đối)."""
    chu_tren_man_hinh = cau.get("chuTrenManHinh") or cau.get("loi", "")[:40]
    loi = cau.get("loi", "")
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": HYPERFRAMES_SCENE_PROMPT.format(
                chu_tren_man_hinh=chu_tren_man_hinh, loi=loi,
                y_do_hinh=cau.get("yDoHinh", ""), duration=round(duration, 2),
            )}],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        ai_html = data.get("html", "")
        ai_gsap = data.get("gsap", [])
        if not ai_html or not isinstance(ai_gsap, list):
            return None
        # Guard: chữ tiêu đề/lời đọc phải xuất hiện nguyên văn — chặn AI paraphrase/bịa chữ mới
        if chu_tren_man_hinh and chu_tren_man_hinh not in ai_html:
            return None
        if loi and loi not in ai_html:
            return None
        if any(bad in ai_html for bad in ("<script", "Math.random", "Date.now", "fetch(")):
            return None
        if any(not isinstance(line, str) or not line.strip().startswith("tl.") for line in ai_gsap):
            return None
        return {"html": ai_html, "gsap": "\n      ".join(ai_gsap)}
    except Exception as e:
        print(f"[HyperFrames AI] Sinh scene lỗi, dùng bản mẫu an toàn thay thế: {e}")
        return None


def build_ai_scene_html(ai_content: dict, duration: float) -> str:
    fade_out_start = max(duration - 0.4, 0.1)
    return AI_SCENE_WRAPPER.format(
        duration=duration, ai_html=ai_content["html"], ai_gsap=ai_content["gsap"],
        fade_out_start=fade_out_start,
    )


def validate_scene(project_dir: str) -> bool:
    """Chạy hyperframes check (lint + runtime JS thật + layout + contrast) — trả False nếu
    AI viết code JS lỗi/hỏng bố cục, để nơi gọi rớt về bản mẫu an toàn thay vì render ra
    video hỏng."""
    result = subprocess.run(
        [_bin_path("hyperframes"), "check", project_dir],
        capture_output=True, env=_run_env(),
    )
    return result.returncode == 0


def render_scene_video(project_dir: str, out_mp4: str) -> None:
    subprocess.run(
        [_bin_path("hyperframes"), "render", project_dir, "-o", out_mp4, "--quiet"],
        check=True, capture_output=True, env=_run_env(),
    )


def init_project(project_dir: str) -> None:
    subprocess.run(
        [_bin_path("hyperframes"), "init", os.path.basename(project_dir), "--example", "blank",
         "--non-interactive", "--resolution=landscape"],
        check=True, capture_output=True, env=dict(_run_env(), HYPERFRAMES_SKIP_SKILLS="1"),
        cwd=os.path.dirname(project_dir),
    )


def render(kich_ban: dict, out_mp4: str) -> None:
    cau_list = kich_ban.get("cau", [])
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = os.path.join(tmp, "hf-project")
        init_project(project_dir)

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

            # AI có tính ngẫu nhiên — cùng 1 câu có lúc pass có lúc fail check (phát hiện thật khi
            # test lại nhiều lần). Thử tối đa 3 lần trước khi rớt về bản mẫu an toàn, giống đúng
            # pattern retry 3 lần đã dùng ở /generate (main.py) thay vì rớt ngay sau 1 lần thử.
            index_path = os.path.join(project_dir, "index.html")
            used_ai_scene = False
            for attempt in range(3):
                ai_content = generate_ai_scene(cau, duration)
                if ai_content is None:
                    continue
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(build_ai_scene_html(ai_content, duration))
                if validate_scene(project_dir):
                    used_ai_scene = True
                    break
                print(f"[HyperFrames] Cảnh {n}: AI-designed layout lần {attempt + 1} không qua check, thử lại...")
            if not used_ai_scene:
                print(f"[HyperFrames] Cảnh {n}: hết 3 lần thử, dùng bản mẫu an toàn.")
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(render_scene_html(cau, duration))

            visual_path = os.path.join(tmp, f"v_{i:03d}.mp4")
            kind = "AI tự thiết kế" if used_ai_scene else "bản mẫu cố định"
            print(f"[HyperFrames] render cảnh {n} ({duration:.1f}s, {kind})...")
            render_scene_video(project_dir, visual_path)

            segment_path = os.path.join(tmp, f"s_{i:03d}.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-i", visual_path, "-i", audio_path,
                 "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
                 "-shortest", segment_path],
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
        print("Dùng: python3 render_video_hyperframes.py <kich_ban.json> <output.mp4>")
        sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    kich_ban = data.get("kichBan", data)
    render(kich_ban, sys.argv[2])
