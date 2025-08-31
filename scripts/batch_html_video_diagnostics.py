#!/usr/bin/env python3
"""
html_to_video_faithful.py — v4
Cel: wierne zgrywanie od t=0. Dwa tryby: klatkowy (domyślny) i CZAS RZECZYWISTY (--realtime) z nagrywaniem w Playwright.

Nowe opcje (vs v3):
--realtime               nagrywaj realtime przez Playwright (WebM → MP4). Rozwiązuje przyspieszone animacje.
--channel chrome         uruchom przeglądarkę systemową Chrome (bliższy rendering jak „na żywo”).

Przykład realtime 1:1:
python html_to_video_faithful.py \
  http://127.0.0.1:8111/i.html \
  out_rt.mp4 2 30 1080 1920 1 \
  --realtime --reload --wait-until networkidle --wait-fonts \
  --ready-selector "body" --encoder libx264 --crf 14 --pixfmt yuv444p --channel chrome
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright


def restart_css_animations(page):
    page.evaluate(
        """
(() => {
  const els = document.querySelectorAll('*');
  for (const el of els) {
    const cs = getComputedStyle(el);
    const hasAnim = cs.animationName !== 'none' && parseFloat(cs.animationDuration) > 0;
    if (hasAnim) el.style.animation = 'none';
  }
  void document.documentElement.offsetHeight;
  for (const el of document.querySelectorAll('*')) {
    if (el.style && el.style.animation === 'none') el.style.animation = '';
  }
})();
"""
    )


def restart_waapi(page):
    page.evaluate(
        """
(() => {
  try {
    const anims = document.getAnimations ? document.getAnimations() : [];
    for (const a of anims) { try { a.cancel(); a.play(); } catch (e) {} }
  } catch(e) {}
})();
"""
    )


def capture_frames(
    url: str,
    duration: float,
    fps: int,
    width: int,
    height: int,
    dpr: int,
    frames_dir: Path,
    wait_until: str = "domcontentloaded",
    timeout_ms: int = 60000,
    reload_before: bool = False,
    do_restart_css: bool = False,
    do_restart_waapi: bool = False,
    click_selector: Optional[str] = None,
    pre_js: Optional[str] = None,
    pre_wait_ms: int = 0,
    ready_selector: Optional[str] = None,
    ready_timeout_ms: int = 15000,
    wait_fonts: bool = False,
    log_console: bool = False,
    channel: Optional[str] = None,
) -> int:
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_frames = int(round(duration * fps))

    with sync_playwright() as p:
        launch_kwargs = dict(headless=True, args=[
            "--force-color-profile=srgb",
            "--enable-gpu-rasterization",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
        ])
        if channel:
            launch_kwargs["channel"] = channel
        browser = p.chromium.launch(**launch_kwargs)

        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
            ),
        )
        page = context.new_page()

        if log_console:
            page.on("console", lambda msg: print(f"[console] {msg.type()}: {msg.text()}", file=sys.stderr))
            page.on("pageerror", lambda exc: print(f"[pageerror] {exc}", file=sys.stderr))

        if url.startswith("http://") or url.startswith("https://"):
            page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        else:
            abs_path = Path(url).resolve()
            page.goto(f"file://{abs_path}", wait_until=wait_until, timeout=timeout_ms)

        if reload_before:
            page.reload(wait_until=wait_until, timeout=timeout_ms)

        if pre_js:
            page.evaluate(pre_js)
        if click_selector:
            try:
                page.click(click_selector, timeout=2000)
            except Exception as e:
                print(f"[warn] click failed: {e}", file=sys.stderr)
        if wait_fonts:
            page.evaluate("""
                () => new Promise(r => {
                  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => r(true));
                  else r(false);
                })
            """)
        if ready_selector:
            page.wait_for_selector(ready_selector, state="visible", timeout=ready_timeout_ms)
        if do_restart_css:
            restart_css_animations(page)
        if do_restart_waapi:
            restart_waapi(page)
        if pre_wait_ms > 0:
            page.wait_for_timeout(pre_wait_ms)

        interval_s = 1.0 / fps
        t0 = time.perf_counter()
        saved = 0
        for i in range(total_frames):
            frame_path = frames_dir / f"frame_{i:06d}.png"
            page.screenshot(
                path=str(frame_path),
                clip={"x": 0, "y": 0, "width": width, "height": height},
                animations="allow",
            )
            saved += 1
            target = t0 + (i + 1) * interval_s
            now = time.perf_counter()
            remain = max(0.0, target - now)
            if remain > 0:
                page.wait_for_timeout(remain * 1000.0)

        context.close()
        browser.close()

    return saved


def capture_realtime(
    url: str,
    duration: float,
    fps: int,
    width: int,
    height: int,
    dpr: int,
    wait_until: str,
    timeout_ms: int,
    reload_before: bool,
    click_selector: Optional[str],
    pre_js: Optional[str],
    pre_wait_ms: int,
    ready_selector: Optional[str],
    ready_timeout_ms: int,
    wait_fonts: bool,
    log_console: bool,
    channel: Optional[str],
    tmp_dir: Path,
) -> Path:
    with sync_playwright() as p:
        launch_kwargs = dict(headless=True)
        if channel:
            launch_kwargs["channel"] = channel
        browser = p.chromium.launch(**launch_kwargs)

        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
            record_video_dir=str(tmp_dir),
            record_video_size={"width": width, "height": height},
        )
        page = context.new_page()

        if log_console:
            page.on("console", lambda msg: print(f"[console] {msg.type()}: {msg.text()}", file=sys.stderr))
            page.on("pageerror", lambda exc: print(f"[pageerror] {exc}", file=sys.stderr))

        if url.startswith("http://") or url.startswith("https://"):
            page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        else:
            abs_path = Path(url).resolve()
            page.goto(f"file://{abs_path}", wait_until=wait_until, timeout=timeout_ms)

        if reload_before:
            page.reload(wait_until=wait_until, timeout=timeout_ms)

        if pre_js:
            page.evaluate(pre_js)
        if click_selector:
            try:
                page.click(click_selector, timeout=2000)
            except Exception as e:
                print(f"[warn] click failed: {e}", file=sys.stderr)
        if wait_fonts:
            page.evaluate("""
                () => new Promise(r => {
                  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => r(true));
                  else r(false);
                })
            """)
        if ready_selector:
            page.wait_for_selector(ready_selector, state="visible", timeout=ready_timeout_ms)
        if pre_wait_ms > 0:
            page.wait_for_timeout(pre_wait_ms)

        page.wait_for_timeout(duration * 1000)
        page.close()  # to finalize recording
        webm_path = page.video.path()
        context.close()
        browser.close()
        return Path(webm_path)


def encode_video(
    frames_dir: Path,
    output_path: Path,
    fps: int,
    width: int,
    height: int,
    encoder: str,
    crf: Optional[int],
    pixfmt: Optional[str],
    preset: str,
    lossless: bool,
) -> None:
    vf = f"scale={width}:{height}:flags=lanczos+accurate_rnd+full_chroma_int"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%06d.png"),
        "-vf", vf,
        "-c:v", encoder,
        "-movflags", "+faststart",
    ]

    if encoder == "libx264rgb":
        cmd += ["-preset", "slower", "-pix_fmt", "rgb24"]
        cmd += ["-crf", "0" if lossless else str(crf if crf is not None else 14)]
    else:
        if encoder == "libx264":
            cmd += ["-preset", "slower", "-crf", str(crf if crf is not None else 14)]
        elif encoder in ("h264_nvenc", "hevc_nvenc"):
            cmd += ["-preset", "p7", "-cq", str(crf if crf is not None else 14)]
        if pixfmt:
            cmd += ["-pix_fmt", pixfmt]

    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)


def encode_webm_to_mp4(webm_path: Path, output_path: Path, encoder: str, crf: Optional[int], pixfmt: Optional[str]):
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(webm_path), "-c:v", encoder,
    ]
    if encoder == "libx264":
        cmd += ["-crf", str(crf if crf is not None else 14)]
    if pixfmt:
        cmd += ["-pix_fmt", pixfmt]
    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Zgrywacz HTML → wideo/PNG; tryb klatkowy i realtime.")
    ap.add_argument("url")
    ap.add_argument("output")
    ap.add_argument("duration", type=float)
    ap.add_argument("fps", type=int)
    ap.add_argument("width", type=int)
    ap.add_argument("height", type=int)
    ap.add_argument("dpr", type=int, nargs="?", default=2)

    ap.add_argument("--frames-only", action="store_true")
    ap.add_argument("--frames-dir", default="frames_faithful")
    ap.add_argument("--keep-frames", action="store_true")

    ap.add_argument("--encoder", default="libx264")
    ap.add_argument("--crf", type=int, default=None)
    ap.add_argument("--pixfmt", default="yuv444p")
    ap.add_argument("--preset", default="slower")
    ap.add_argument("--lossless", action="store_true")

    ap.add_argument("--wait-until", default="domcontentloaded")
    ap.add_argument("--timeout-ms", type=int, default=60000)

    ap.add_argument("--reload", action="store_true")
    ap.add_argument("--restart-css", action="store_true")
    ap.add_argument("--restart-waapi", action="store_true")
    ap.add_argument("--click", default=None)
    ap.add_argument("--pre-js", default=None)
    ap.add_argument("--pre-wait-ms", type=int, default=0)
    ap.add_argument("--ready-selector", default=None)
    ap.add_argument("--ready-timeout-ms", type=int, default=15000)
    ap.add_argument("--wait-fonts", action="store_true")
    ap.add_argument("--log-console", action="store_true")

    ap.add_argument("--realtime", action="store_true")
    ap.add_argument("--channel", default=None)

    args = ap.parse_args()

    try:
        if args.realtime:
            tmp_dir = Path(".html2video_tmp")
            tmp_dir.mkdir(exist_ok=True)
            webm = capture_realtime(
                url=args.url,
                duration=args.duration,
                fps=args.fps,
                width=args.width,
                height=args.height,
                dpr=args.dpr,
                wait_until=args.wait_until,
                timeout_ms=args.timeout_ms,
                reload_before=args.reload,
                click_selector=args.click,
                pre_js=args.pre_js,
                pre_wait_ms=args.pre_wait_ms,
                ready_selector=args.ready_selector,
                ready_timeout_ms=args.ready_timeout_ms,
                wait_fonts=args.wait_fonts,
                log_console=args.log_console,
                channel=args.channel,
                tmp_dir=tmp_dir,
            )
            encode_webm_to_mp4(webm, Path(args.output), args.encoder, args.crf, args.pixfmt)
            print(f"Wideo zapisane (realtime): {args.output}")
            return 0

        frames_dir = Path(args.frames_dir)
        saved = capture_frames(
            url=args.url,
            duration=args.duration,
            fps=args.fps,
            width=args.width,
            height=args.height,
            dpr=args.dpr,
            frames_dir=frames_dir,
            wait_until=args.wait_until,
            timeout_ms=args.timeout_ms,
            reload_before=args.reload,
            do_restart_css=args.restart_css,
            do_restart_waapi=args.restart_waapi,
            click_selector=args.click,
            pre_js=args.pre_js,
            pre_wait_ms=args.pre_wait_ms,
            ready_selector=args.ready_selector,
            ready_timeout_ms=args.ready_timeout_ms,
            wait_fonts=args.wait_fonts,
            log_console=args.log_console,
            channel=args.channel,
        )

        if args.frames_only:
            print(f"PNG: {saved} klatek → {frames_dir}")
            return 0

        encode_video(
            frames_dir=frames_dir,
            output_path=Path(args.output),
            fps=args.fps,
            width=args.width,
            height=args.height,
            encoder=args.encoder,
            crf=args.crf,
            pixfmt=args.pixfmt,
            preset=args.preset,
            lossless=args.lossless,
        )
        print(f"Wideo zapisane: {args.output}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return 1
    except Exception as e:
        print(f"Błąd: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
