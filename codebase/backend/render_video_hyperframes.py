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
import queue
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from render_video import audio_duration_sec, make_silence, tts_to_file
from render_video import client as openai_client
from prompt import HYPERFRAMES_FIX_PROMPT, HYPERFRAMES_SCENE_PROMPT

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

# Khung thương hiệu CỐ ĐỊNH (do code kiểm soát, không để AI tự bịa mỗi cảnh) — dùng chung cho cả
# bản mẫu an toàn lẫn cảnh do AI thiết kế, để mọi cảnh trong video nhìn LIỀN MẠCH thay vì rời rạc.
# Học từ guide chính thức của HyperFrames (hyperframes.heygen.com/guides/prompting +
# github.com/heygen-com/hyperframes/blob/main/docs/guides/claude-design-hyperframes.md): dùng
# design tokens :root dùng chung, giữ khung thương hiệu (eyebrow/accent-bar/caption card) cố định
# qua mọi cảnh, để phần AI tự thiết kế chỉ còn đúng 1 việc — sơ đồ minh hoạ — thu hẹp bề mặt lỗi.
_CHROME_STYLE = """
      :root {
        --bg:#0A0A0F; --ink:#F5F5F5; --accent:#58C4DD; --accent2:#FFC857; --muted:#B7B7C2; --card:#16161F;
      }
      #chrome-eyebrow {
        position: absolute; left: 96px; top: 88px;
        color: var(--accent); font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 26px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
        opacity: 0;
      }
      #chrome-accent-bar {
        position: absolute; left: 96px; top: 132px; width: 110px; height: 6px;
        background: var(--accent); border-radius: 4px; transform-origin: left;
      }
      #chrome-headline {
        position: absolute; left: 96px; top: 164px; width: 1400px;
        color: var(--ink); font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 56px; font-weight: 900; line-height: 1.2;
        opacity: 0;
      }
      #chrome-source-tag {
        position: absolute; right: 96px; top: 88px;
        color: var(--muted); font-size: 20px;
        background: var(--card); padding: 8px 18px; border-radius: 100px;
        opacity: 0;
      }
      #chrome-caption-bar {
        position: absolute; left: 96px; right: 96px; bottom: 64px;
        min-height: 96px; background: var(--card); border-radius: 20px;
        display: flex; align-items: center; gap: 20px; padding: 24px 32px;
        opacity: 0;
      }
      #chrome-caption-icon {
        flex: none; width: 44px; height: 44px; border-radius: 50%;
        background: var(--accent); color: var(--bg);
        display: flex; align-items: center; justify-content: center; font-size: 22px;
      }
      #chrome-caption-text {
        color: var(--ink); font-size: 30px; line-height: 1.5;
      }
      #ai-content {
        position: absolute; left: 96px; top: 300px; width: 1728px; height: 440px;
        overflow: hidden;
      }
"""


def _chrome_html(headline: str, caption: str, eyebrow: str, source_tag: str, duration: float) -> str:
    source_tag_html = ""
    if source_tag:
        source_tag_html = (
            f'<p id="chrome-source-tag" class="clip" data-start="0" '
            f'data-duration="{duration}">{html.escape(source_tag)}</p>'
        )
    return (
        f'<p id="chrome-eyebrow" class="clip" data-start="0" data-duration="{duration}">'
        f'{html.escape(eyebrow)}</p>\n'
        f'<div id="chrome-accent-bar" class="clip" data-start="0" data-duration="{duration}"></div>\n'
        f'<h1 id="chrome-headline" class="clip" data-start="0" data-duration="{duration}">'
        f'{html.escape(headline)}</h1>\n'
        f'{source_tag_html}\n'
        f'<div id="chrome-caption-bar" class="clip" data-start="0" data-duration="{duration}">\n'
        f'  <div id="chrome-caption-icon">'
        f'<svg width="20" height="20" viewBox="0 0 24 24"><path fill="#0A0A0F" '
        f'd="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-.77-3.29-2-4.24v8.48c1.23-.95 2-2.47 2-4.24z"/>'
        f'</svg></div>\n'
        f'  <div id="chrome-caption-text">{html.escape(caption)}</div>\n'
        f'</div>'
    )


def _chrome_gsap(fade_out_start: float, has_source_tag: bool = True) -> str:
    lines = [
        'tl.to("#chrome-eyebrow", {opacity:1,duration:0.4}, 0.1);',
        'tl.fromTo("#chrome-accent-bar", {scaleX:0}, {scaleX:1,duration:0.5}, 0.3);',
        'tl.fromTo("#chrome-headline", {opacity:0,y:24}, {opacity:1,y:0,duration:0.6}, 0.4);',
    ]
    if has_source_tag:
        lines.append('tl.to("#chrome-source-tag", {opacity:1,duration:0.4}, 0.6);')
    lines.append('tl.fromTo("#chrome-caption-bar", {opacity:0,y:16}, {opacity:1,y:0,duration:0.5}, 1.0);')
    lines.append(f'tl.to("#root", {{opacity:0,duration:0.35}}, {fade_out_start});')
    return "\n      ".join(lines)


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
      {chrome_style}
      #safe-ring {{
        position: absolute; left: 50%; top: 50%; width: 260px; height: 260px;
        margin: -130px 0 0 -130px; border-radius: 50%;
        border: 2px solid var(--accent); opacity: 0;
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
      {chrome_html}
      <div id="ai-content" class="clip" data-start="0" data-duration="{duration}">
        <div id="safe-ring" class="clip" data-start="0" data-duration="{duration}"></div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chrome_gsap}
      tl.fromTo("#safe-ring", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 0.5, scale: 1, duration: 1.2, ease: "power2.out" }}, 0.6);
      tl.to("#safe-ring", {{ scale: 1.05, duration: 2, ease: "sine.inOut", yoyo: true, repeat: 999 }}, 1.8);

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
    headline = cau.get("chuTrenManHinh") or cau.get("loi", "")[:40]
    caption = cau.get("loi", "")
    eyebrow = "ScriptScout"
    goi_y = cau.get("goiYHienNguon", "")
    fade_out_start = max(duration - 0.4, 0.1)
    chrome_html = _chrome_html(headline, caption, eyebrow, goi_y, duration)
    return SCENE_TEMPLATE.format(
        duration=duration, chrome_style=_CHROME_STYLE, chrome_html=chrome_html,
        chrome_gsap=_chrome_gsap(fade_out_start, has_source_tag=bool(goi_y)),
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
      {chrome_style}
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
      {chrome_html}
      <div id="ai-content" class="clip" data-start="0" data-duration="{duration}">
        {ai_html}
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chrome_gsap}
      {ai_gsap}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


def generate_ai_scene(cau: dict, duration: float) -> dict | None:
    """Cho AI tự thiết kế bố cục cảnh (đa dạng hơn 1 template cố định), guard chặt: bắt buộc
    tiêu đề/phụ đề/nguồn giờ do KHUNG THƯƠNG HIỆU CỐ ĐỊNH đảm nhiệm (_chrome_html/_chrome_gsap,
    render y hệt cho mọi cảnh, không thể sai), nên AI chỉ còn đúng 1 việc: vẽ SƠ ĐỒ minh hoạ bên
    trong vùng #ai-content (1728x440, toạ độ 0,0 là góc trên-trái vùng này). Thu hẹp việc AI phải
    làm giúp giảm bề mặt lỗi (không cần guard chữ nguyên văn nữa vì AI không tự render chữ tiêu
    đề/phụ đề). Trả về None nếu AI lỗi/vi phạm ràng buộc kỹ thuật, để nơi gọi tự rớt về
    render_scene_html() (bản mẫu cố định, an toàn tuyệt đối).

    Model gpt-5.4-mini (không phải gpt-4o-mini): thiết kế sơ đồ đòi hỏi vừa tuân thủ nhiều ràng
    buộc kỹ thuật (toạ độ, JSON, quy tắc thẻ/card) vừa cần óc sáng tạo minh hoạ đúng nghĩa (vd vẽ
    HÌNH NGÔI NHÀ thật thay vì chỉ 1 khung chữ nhật có chữ) — gpt-4o-mini pass hết check kỹ thuật
    nhưng thường chọn thiết kế nhạt/chung chung. Đúng bài học đã có ở bước expand-script (case 33,
    golden-set.md): đổi model thế hệ mới hơn cho bước cần sáng tạo giải quyết được phần lớn vấn đề
    mà siết prompt thêm không giải quyết nổi."""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": HYPERFRAMES_SCENE_PROMPT.format(
                chu_tren_man_hinh=cau.get("chuTrenManHinh") or cau.get("loi", "")[:40],
                loi=cau.get("loi", ""),
                y_do_hinh=cau.get("yDoHinh", ""), duration=round(duration, 2),
            )}],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        ai_html = data.get("html", "")
        ai_gsap = data.get("gsap", [])
        if not ai_html or not isinstance(ai_gsap, list):
            return None
        if any(bad in ai_html for bad in ("<script", "Math.random", "Date.now", "fetch(")):
            return None
        if any(not isinstance(line, str) or not line.strip().startswith("tl.") for line in ai_gsap):
            return None
        return {"html": ai_html, "gsap": "\n      ".join(ai_gsap)}
    except Exception as e:
        print(f"[HyperFrames AI] Sinh scene lỗi, dùng bản mẫu an toàn thay thế: {e}")
        return None


def build_ai_scene_html(cau: dict, ai_content: dict, duration: float) -> str:
    fade_out_start = max(duration - 0.4, 0.1)
    headline = cau.get("chuTrenManHinh") or cau.get("loi", "")[:40]
    caption = cau.get("loi", "")
    goi_y = cau.get("goiYHienNguon", "")
    chrome_html = _chrome_html(headline, caption, "ScriptScout", goi_y, duration)
    return AI_SCENE_WRAPPER.format(
        duration=duration, chrome_style=_CHROME_STYLE, chrome_html=chrome_html,
        chrome_gsap=_chrome_gsap(fade_out_start, has_source_tag=bool(goi_y)),
        ai_html=ai_content["html"], ai_gsap=ai_content["gsap"],
    )


def check_scene(project_dir: str) -> dict:
    """Chạy `hyperframes check --json` (đầy đủ browser: lint+runtime+layout+motion+contrast).
    KHÁC lint_scene(): mỗi mục con (lint/runtime/layout/motion/contrast) đều có "findings" CÙNG
    CẤU TRÚC (code/message/selector/fixHint) — nhiều lỗi thật (tràn khung, tương phản, JS runtime)
    CHỈ xuất hiện ở đây, lint tĩnh không thấy được. Trả {"ok": bool, "findings": [...đã gộp...]}."""
    result = subprocess.run(
        [_bin_path("hyperframes"), "check", project_dir, "--json"],
        capture_output=True, env=_run_env(), text=True,
    )
    try:
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return {"ok": result.returncode == 0, "findings": []}
    findings = []
    for section in ("lint", "runtime", "layout", "motion", "contrast"):
        findings.extend(data.get(section, {}).get("findings", []))
    return {"ok": data.get("ok", False), "findings": findings}


def lint_scene(project_dir: str) -> dict:
    """Chạy `hyperframes lint --json` — CHỈ ~1.3s (không mở trình duyệt) so với ~6.7s của
    `check` đầy đủ, dùng làm vòng lặp tự-sửa NHANH trước khi tốn browser cho check cuối cùng.
    Trả {"ok": bool, "findings": [...]} — findings có code/message/selector/fixHint thật."""
    result = subprocess.run(
        [_bin_path("hyperframes"), "lint", project_dir, "--json"],
        capture_output=True, env=_run_env(), text=True,
    )
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return {"ok": result.returncode == 0, "findings": []}


def fix_ai_scene(cau: dict, duration: float, ai_content: dict, findings: list[dict]) -> dict | None:
    """Cho AI sửa ĐÚNG lỗi lint thật báo về (code/message/fixHint), thay vì đoán lại từ đầu như
    retry mù trước đây — nhanh hơn nhiều vì input đã có sẵn bản thiết kế cũ, AI chỉ vá chỗ sai."""
    findings_text = "\n".join(
        f"- [{f.get('code', '?')}] {f.get('selector', '')}: {f.get('message', '')}"
        f" — Cách sửa gợi ý: {f.get('fixHint', '')}"
        for f in findings
    ) or "(không có chi tiết lỗi)"
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": HYPERFRAMES_FIX_PROMPT.format(
                current_html=ai_content["html"], current_gsap=ai_content["gsap"],
                findings_text=findings_text,
            )}],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        ai_html = data.get("html", "")
        ai_gsap = data.get("gsap", [])
        if not ai_html or not isinstance(ai_gsap, list):
            return None
        if any(bad in ai_html for bad in ("<script", "Math.random", "Date.now", "fetch(")):
            return None
        if any(not isinstance(line, str) or not line.strip().startswith("tl.") for line in ai_gsap):
            return None
        return {"html": ai_html, "gsap": "\n      ".join(ai_gsap)}
    except Exception as e:
        print(f"[HyperFrames AI] Sửa lỗi scene thất bại: {e}")
        return None


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


def _process_one_scene(i: int, cau: dict, tmp: str, project_dir: str) -> str:
    """Xử lý ĐÚNG 1 câu — tách riêng khỏi render() để chạy song song được. Mỗi lời gọi hàm này
    PHẢI nhận 1 project_dir RIÊNG (không dùng chung giữa các luồng cùng lúc), vì mỗi lần ghi đè
    index.html của chính project đó rồi mới render — 2 luồng dùng chung 1 project sẽ ghi đè lẫn
    nhau, ra video sai cảnh."""
    n = cau.get("n", i)
    audio_path = os.path.join(tmp, f"a_{i:03d}.mp3")
    if cau.get("loi"):
        print(f"[TTS] câu {n}: {cau['loi'][:50]}...")
        tts_to_file(cau["loi"], audio_path)
        duration = audio_duration_sec(audio_path)
    else:
        duration = float(cau.get("dungGiay", SILENCE_DEFAULT_SEC))
        make_silence(audio_path, duration)

    # Vòng tự-sửa 2 tầng (nhanh + giữ được thiết kế đẹp thay vì bỏ đi sinh lại từ đầu):
    # Tầng 1 — lint --json (~1.3s, không mở trình duyệt): vá nhanh lỗi cấu trúc/GSAP tĩnh.
    # Tầng 2 — check --json (~6.7s, có trình duyệt) SAU KHI lint sạch: bắt lỗi runtime/layout/
    # contrast mà lint tĩnh không thấy được (đa số lỗi thật nằm ở đây, không phải lint — quan sát
    # thật khi test) — feed đúng finding thật (code/message/fixHint) cho AI vá, KHÔNG bỏ thiết kế
    # đi sinh lại mù như bản cũ. Chỉ sinh lại từ đầu khi vá hết số lần cho phép vẫn còn lỗi.
    index_path = os.path.join(project_dir, "index.html")
    used_ai_scene = False
    for gen_round in range(2):
        ai_content = generate_ai_scene(cau, duration)
        if ai_content is None:
            continue
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(build_ai_scene_html(cau, ai_content, duration))

        lint_result = lint_scene(project_dir)
        for fix_attempt in range(2):
            if lint_result.get("ok"):
                break
            findings = lint_result.get("findings", [])
            print(f"[HyperFrames] Cảnh {n}: lint thấy {len(findings)} lỗi, cho AI vá lần {fix_attempt + 1}...")
            fixed = fix_ai_scene(cau, duration, ai_content, findings)
            if fixed is None:
                break
            ai_content = fixed
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(build_ai_scene_html(cau, ai_content, duration))
            lint_result = lint_scene(project_dir)

        if not lint_result.get("ok"):
            print(f"[HyperFrames] Cảnh {n}: vòng sinh {gen_round + 1} vẫn còn lỗi lint, thử sinh lại...")
            continue

        check_result = check_scene(project_dir)
        for fix_attempt in range(2):
            if check_result.get("ok"):
                break
            findings = check_result.get("findings", [])
            print(f"[HyperFrames] Cảnh {n}: check thấy {len(findings)} lỗi, cho AI vá lần {fix_attempt + 1}...")
            fixed = fix_ai_scene(cau, duration, ai_content, findings)
            if fixed is None:
                break
            ai_content = fixed
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(build_ai_scene_html(cau, ai_content, duration))
            check_result = check_scene(project_dir)

        if check_result.get("ok"):
            used_ai_scene = True
            break
        print(f"[HyperFrames] Cảnh {n}: vòng sinh {gen_round + 1} vá hết lượt vẫn còn lỗi check, thử sinh lại...")
    if not used_ai_scene:
        print(f"[HyperFrames] Cảnh {n}: hết các vòng thử, dùng bản mẫu an toàn.")
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
    return segment_path


def render(kich_ban: dict, out_mp4: str, max_workers: int = 6) -> None:
    """Chạy SONG SONG nhiều câu cùng lúc (mặc định 6 luồng) thay vì tuần tự từng câu — mỗi câu
    độc lập hoàn toàn (TTS + AI thiết kế + render riêng), chỉ cần ghép nối đúng THỨ TỰ ở bước
    cuối. Tốc độ tổng thể tăng gần đúng theo số luồng (máy 12 core, nhưng RAM THẬT khả dụng lúc đo
    chỉ ~6.7GB do máy đang chạy nhiều app khác — mỗi luồng ăn ~300-400MB cho 1 Chrome headless
    riêng, 6 luồng ~2-2.4GB vẫn an toàn). Tăng max_workers nếu máy rảnh hơn/nhiều RAM hơn, giảm
    nếu thấy hết RAM/CPU quá tải (kiểm bằng `free -h` trước khi tăng)."""
    cau_list = kich_ban.get("cau", [])
    n_workers = min(max_workers, len(cau_list)) or 1
    with tempfile.TemporaryDirectory() as tmp:
        # Tạo trước n_workers project riêng biệt, đưa vào hàng đợi — mỗi luồng mượn 1 project,
        # xong câu thì trả lại hàng đợi cho luồng khác dùng tiếp (tránh ghi đè lẫn nhau).
        dir_pool: "queue.Queue[str]" = queue.Queue()
        for w in range(n_workers):
            project_dir = os.path.join(tmp, f"hf-project-{w}")
            init_project(project_dir)
            dir_pool.put(project_dir)

        def _worker(i: int, cau: dict) -> tuple[int, str]:
            project_dir = dir_pool.get()
            try:
                return i, _process_one_scene(i, cau, tmp, project_dir)
            finally:
                dir_pool.put(project_dir)

        results: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            futures = [pool.submit(_worker, i, cau) for i, cau in enumerate(cau_list)]
            for fut in as_completed(futures):
                i, segment_path = fut.result()
                results[i] = segment_path

        segment_paths = [results[i] for i in range(len(cau_list))]

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
