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
import base64
import glob
import html
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from render_video import audio_duration_sec, make_silence, tts_to_file
from render_video import client as openai_client
from prompt import HYPERFRAMES_FIX_PROMPT, HYPERFRAMES_QUALITY_JUDGE_PROMPT, HYPERFRAMES_SCENE_PROMPT

_HOME = os.path.expanduser("~")
_DEFAULT_NODE_BIN = os.path.join(_HOME, ".local/hyperframes-tools/node/bin")
_DEFAULT_HF_BIN = os.path.join(_HOME, ".local/hyperframes-tools/npm-global/bin")
# Repo root (2 cấp trên file này: codebase/backend/render_video_hyperframes.py) — cwd khi gọi
# `claude` headless để nó tự tìm thấy .claude/skills/scriptscout-authoring của repo.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CLAUDE_CODE_BIN = shutil.which("claude") or os.path.join(_HOME, ".local/bin/claude")

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
# Bảng màu/phong cách: "VinUni Academic Light Theme" (theo skill scriptscout-authoring của
# teammate DungBallad, github.com/DungBallad/ScoutX-Skills — đội trưởng xác nhận dùng nền sáng
# thay 3Blue1Brown dark trước đây), giữ nguyên brand chữ "ScriptScout" của mình (không đổi thành
# tên khoá của skill gốc), chỉ áp dụng bảng màu + quy tắc "không dùng emoji hệ điều hành".
_CHROME_STYLE = """
      :root {
        --bg:#FFFFFF; --bg-canvas:#F8FAFC; --ink:#1E293B; --muted:#475569;
        --heading:#0C2340; --accent:#2563EB; --accent-red:#C5221F; --card:#F0F6FC;
        --gold:#D97706; --emerald:#059669;
      }
      #chrome-eyebrow {
        position: absolute; left: 96px; top: 88px;
        color: var(--accent-red); font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 26px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase;
        opacity: 0;
      }
      #chrome-accent-bar {
        position: absolute; left: 96px; top: 132px; width: 110px; height: 6px;
        background: var(--accent-red); border-radius: 4px; transform-origin: left;
      }
      #chrome-headline {
        position: absolute; left: 96px; top: 164px; width: 1400px;
        color: var(--heading); font-family: 'Space Grotesk', Arial, sans-serif;
        font-size: 56px; font-weight: 800; line-height: 1.2;
        opacity: 0;
      }
      #chrome-source-tag {
        position: absolute; right: 96px; top: 88px;
        color: var(--muted); font-size: 20px;
        background: var(--card); border: 1px solid rgba(37,99,235,0.3);
        padding: 8px 18px; border-radius: 100px;
        opacity: 0;
      }
      #chrome-caption-bar {
        position: absolute; left: 96px; right: 96px; bottom: 48px; max-height: 96px;
        background: rgba(255,255,255,0.95); border: 1px solid rgba(148,163,184,0.4);
        border-radius: 16px; overflow: hidden; box-shadow: 0 15px 35px rgba(15,23,42,0.12);
        display: flex; align-items: center; gap: 16px; padding: 12px 28px;
        opacity: 0;
      }
      #chrome-caption-icon {
        flex: none; width: 36px; height: 36px; border-radius: 50%;
        background: var(--accent); color: #FFFFFF;
        display: flex; align-items: center; justify-content: center; font-size: 18px;
      }
      #chrome-caption-text {
        color: var(--heading); font-size: 22px; font-weight: 600; line-height: 1.35;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
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
        f'<svg width="20" height="20" viewBox="0 0 24 24"><path fill="#FFFFFF" '
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
        background: #FFFFFF;
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
        background: #FFFFFF;
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


def snapshot_scene(project_dir: str, at_seconds: float) -> str | None:
    """Chụp 1 khung hình thật của cảnh tại thời điểm at_seconds bằng `hyperframes snapshot` — dùng
    để đưa cho AI-chấm-chất-lượng NHÌN THẬT, không phải đoán qua HTML/CSS. Trả None nếu chụp lỗi."""
    snap_dir = os.path.join(project_dir, "snapshots")
    for old in glob.glob(os.path.join(snap_dir, "*.png")):
        os.remove(old)
    subprocess.run(
        [_bin_path("hyperframes"), "snapshot", project_dir, "--at", str(at_seconds), "--no-end"],
        capture_output=True, env=_run_env(),
    )
    pngs = sorted(glob.glob(os.path.join(snap_dir, "*.png")))
    return pngs[-1] if pngs else None


def judge_scene_quality(cau: dict, image_path: str) -> dict:
    """Dual-Model Separation (học từ skill video-qa của teammate DungBallad,
    github.com/DungBallad/ScoutX-Skills): model CHẤM phải KHÁC model TẠO (gpt-4o thay vì
    gpt-5.4-mini đang thiết kế cảnh) để tránh thiên kiến tự khen bài chính mình. Bắt lỗi mà
    `hyperframes check` không thấy được vì hợp lệ về kỹ thuật nhưng sai về nội dung/thẩm mỹ: ô
    trống không chữ, chồng lấn nhìn rối, sơ đồ lạc đề. Lỗi/không đọc được ảnh thì coi như đạt
    (fail-open, không chặn nhầm luồng chính)."""
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": HYPERFRAMES_QUALITY_JUDGE_PROMPT.format(
                    chu_tren_man_hinh=cau.get("chuTrenManHinh") or cau.get("loi", "")[:40],
                    loi=cau.get("loi", ""), y_do_hinh=cau.get("yDoHinh", ""),
                )},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "high"}},
            ]}],
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        return {"dat": bool(result.get("dat", True)), "vanDe": result.get("vanDe", [])}
    except Exception as e:
        print(f"[HyperFrames AI] Chấm chất lượng sáng tạo lỗi, coi như đạt: {e}")
        return {"dat": True, "vanDe": []}


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


def generate_scene_via_claude_code(cau: dict, duration: float, project_dir: str) -> bool:
    """Dùng AGENT CODE THẬT (Claude Code headless, lệnh `claude -p`) để thiết kế 1 cảnh — khác hẳn
    generate_ai_scene() (1 lượt gọi API hoàn thiện, không tự kiểm/tự sửa được gì ngoài JSON trả
    về). Claude Code tự ĐỌC/GHI file, tự CHẠY `hyperframes check`, tự đọc lỗi thật và sửa lặp lại
    — đúng cách 1 người lập trình thật làm (và đúng cách suy đoán cảnh mẫu chất lượng cao của
    teammate DungBallad được tạo ra). Test trực tiếp: pass sạch ngay lần thử đầu, 47/47 WCAG AA,
    chất lượng vượt hẳn generate_ai_scene() (xem golden-set.md).

    CẢNH BÁO GIỚI HẠN THẬT (không né): `claude` CLI ở đây đăng nhập bằng tài khoản Pro CÁ NHÂN
    (claude.ai OAuth), không phải Anthropic API key tính phí theo lượt — dùng để tự làm video demo
    thì ổn, nhưng KHÔNG phù hợp cho sản phẩm thật phục vụ nhiều người dùng đồng thời (vượt giới hạn
    dùng của gói cá nhân, sai mục đích gói Pro). Mỗi lượt gọi cũng CHẬM hơn nhiều so với 1 API call
    (agent tự lặp nhiều bước) — cân nhắc giảm max_workers khi bật đường này để tránh quá tải.

    Trả False nếu `claude` CLI không có/lỗi/timeout — nơi gọi tự rớt về generate_ai_scene() (đường
    API cũ) làm phương án dự phòng, không làm hỏng cả pipeline."""
    if not _CLAUDE_CODE_BIN or not os.path.exists(_CLAUDE_CODE_BIN):
        return False

    task = f"""Dùng skill scriptscout-authoring (đọc kỹ references/theme-guidelines.md để lấy đúng bảng màu VinUni Academic Light, cấm emoji) để thiết kế 1 cảnh HyperFrames hoàn chỉnh.

Câu kịch bản cần minh hoạ:
- Tiêu đề: "{cau.get('chuTrenManHinh') or cau.get('loi', '')[:40]}"
- Lời đọc: "{cau.get('loi', '')}"
- Ý đồ hình ảnh: {cau.get('yDoHinh', '')}
- Thời lượng: {round(duration, 2)} giây

Viết 1 file HTML composition HyperFrames HOÀN CHỈNH (có div id=root với data-composition-id/
data-start="0"/data-duration="{round(duration, 2)}"/data-width="1920"/data-height="1080", timeline
GSAP paused tên tl, window.__timelines['main']=tl, canvas 1920x1080, PHẢI có nguyên văn tiêu đề và
lời đọc ở đâu đó trên màn hình) tại đường dẫn tuyệt đối {project_dir}/index.html.

Sau đó chạy lệnh "{_bin_path('hyperframes')} check {project_dir}" để kiểm tra thật, đọc lỗi và tự
sửa file tới khi lệnh đó pass (exit code 0), tối đa 5 lần thử. Không hỏi lại tôi, tự làm tới khi
xong hoặc hết lượt thử."""

    try:
        subprocess.run(
            [_CLAUDE_CODE_BIN, "-p", task,
             "--allowedTools", "Read,Write,Edit,Bash",
             "--permission-mode", "acceptEdits",
             "--max-turns", "30",
             "--output-format", "text"],
            cwd=_REPO_ROOT, env=_run_env(), capture_output=True, timeout=240, text=True,
        )
    except subprocess.TimeoutExpired:
        print("[HyperFrames AI] Claude Code headless timeout, rớt về đường API thường.")
        return False
    except Exception as e:
        print(f"[HyperFrames AI] Claude Code headless lỗi ({e}), rớt về đường API thường.")
        return False

    if not os.path.exists(os.path.join(project_dir, "index.html")):
        return False
    return check_scene(project_dir).get("ok", False)


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

    index_path = os.path.join(project_dir, "index.html")
    used_ai_scene = False

    # Tầng 0 — AGENT CODE THẬT (Claude Code headless), thử TRƯỚC hết: chất lượng cao hơn hẳn
    # đường API bên dưới (test thật: pass sạch ngay lần đầu, 47/47 WCAG AA). Claude Code tự viết
    # NGUYÊN file index.html (không qua build_ai_scene_html/khung chrome cố định — nó tự thiết kế
    # cả phần thương hiệu theo đúng skill), nên khi tầng này thành công thì BỎ QUA toàn bộ vòng
    # tự-sửa API bên dưới. Rớt về tầng API nếu claude CLI không có/lỗi/timeout.
    if generate_scene_via_claude_code(cau, duration, project_dir):
        used_ai_scene = True

    # Vòng tự-sửa 2 tầng qua API (chỉ chạy nếu tầng 0 ở trên thất bại/không có claude CLI):
    # Tầng 1 — lint --json (~1.3s, không mở trình duyệt): vá nhanh lỗi cấu trúc/GSAP tĩnh.
    # Tầng 2 — check --json (~6.7s, có trình duyệt) SAU KHI lint sạch: bắt lỗi runtime/layout/
    # contrast mà lint tĩnh không thấy được (đa số lỗi thật nằm ở đây, không phải lint — quan sát
    # thật khi test) — feed đúng finding thật (code/message/fixHint) cho AI vá, KHÔNG bỏ thiết kế
    # đi sinh lại mù như bản cũ. Chỉ sinh lại từ đầu khi vá hết số lần cho phép vẫn còn lỗi.
    for gen_round in range(2 if not used_ai_scene else 0):
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

        if not check_result.get("ok"):
            print(f"[HyperFrames] Cảnh {n}: vòng sinh {gen_round + 1} vá hết lượt vẫn còn lỗi check, thử sinh lại...")
            continue

        # Tầng 3 — chấm CHẤT LƯỢNG SÁNG TẠO bằng ảnh chụp thật (model khác, gpt-4o) — bắt lỗi mà
        # check kỹ thuật không thấy: ô trống không chữ, chồng lấn nhìn rối, sơ đồ lạc đề. Phát hiện
        # thật (test 5 câu trước khi thêm tầng này): câu 5 pass check sạch ngay lần đầu nhưng có
        # 2 ô trống không chữ — check không có cách nào bắt được loại lỗi này.
        snap_path = snapshot_scene(project_dir, duration / 2)
        judge_result = judge_scene_quality(cau, snap_path) if snap_path else {"dat": True, "vanDe": []}
        for judge_attempt in range(2):
            if judge_result.get("dat"):
                break
            van_de = judge_result.get("vanDe", [])
            print(f"[HyperFrames] Cảnh {n}: AI chấm sáng tạo thấy {len(van_de)} vấn đề, cho AI vá lần {judge_attempt + 1}...")
            findings = [{"code": "chat_luong_sang_tao", "message": vd, "selector": "", "fixHint": ""} for vd in van_de]
            fixed = fix_ai_scene(cau, duration, ai_content, findings)
            if fixed is None:
                break
            ai_content = fixed
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(build_ai_scene_html(cau, ai_content, duration))
            # Vá xong phải re-check kỹ thuật — sửa nội dung có thể vô tình phá layout đã sạch.
            check_result = check_scene(project_dir)
            if not check_result.get("ok"):
                break
            snap_path = snapshot_scene(project_dir, duration / 2)
            judge_result = judge_scene_quality(cau, snap_path) if snap_path else {"dat": True, "vanDe": []}

        if check_result.get("ok") and judge_result.get("dat"):
            used_ai_scene = True
            break
        print(f"[HyperFrames] Cảnh {n}: vòng sinh {gen_round + 1} vẫn chưa đạt chất lượng, thử sinh lại...")
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


def render(kich_ban: dict, out_mp4: str, max_workers: int = 3) -> None:
    """Chạy SONG SONG nhiều câu cùng lúc thay vì tuần tự từng câu — mỗi câu độc lập hoàn toàn
    (TTS + thiết kế cảnh + render riêng), chỉ cần ghép nối đúng THỨ TỰ ở bước cuối.

    Mặc định GIẢM xuống 3 luồng (trước là 6) kể từ khi thêm tầng 0 — Claude Code headless
    (generate_scene_via_claude_code): mỗi lượt gọi nặng hơn nhiều so với 1 API call thường (agent
    tự lặp nhiều bước, có thể mất 1-4 phút/cảnh), và dùng CHUNG 1 tài khoản Pro cá nhân qua CLI
    `claude` — chạy quá nhiều luồng cùng lúc dễ chạm giới hạn dùng của gói cá nhân. Tăng lại nếu
    đã có Anthropic API key riêng cho việc này, giảm nếu thấy bị rate-limit/timeout nhiều."""
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
