"""VideoFetch · download logic (also console mode).

Portable launcher: paths come from this file, never from the folder it is started from.

Project:   VideoFetch v1.1.0
Authors:   Juan Bautista Galisteo Marqués (@juangalisteo)
           Juan Manuel Casado Triguero (@juanmacasado)
License:   GPL-3.0-or-later (see LICENSE)
Copyright (C) 2026 Juan Bautista Galisteo Marqués and Juan Manuel Casado Triguero.
This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License, version 3 or (at your option) any later version.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# Layout: VIDEOFETCH\APP (this file), VIDEOFETCH\SISTEMA (internal parts)
# and VIDEOFETCH\DOWNLOADS (the videos). Paths do not depend on where the folder is.
APP = Path(__file__).resolve().parent
ROOT = APP.parent
LIB = ROOT / "SISTEMA"
DOWNLOADS = ROOT / "DOWNLOADS"
sys.path.insert(0, str(ROOT))  # in case the folder has not been reorganised yet
sys.path.insert(0, str(LIB))
sys.path.insert(0, str(APP))
from idiomas import t, set_language, get_language, LANGUAGES  # noqa: E402  (texts in Spanish and English)

# Social media: named as @username and, if they fail, retried in "incognito mode".
SOCIAL_DOMAINS = ("tiktok.com", "instagram.com", "x.com", "twitter.com", "facebook.com", "fb.watch", "threads.net")

MEDIA_EXT = "mp4|mkv|webm|mov|m4a|mp3|opus|ogg|wav|aac|flac"
FILE_RE = re.compile(
    rf"^(?P<stem>.+?)(?:\.f\d+(?:-\d+)?)?\.(?P<ext>{MEDIA_EXT})(?P<partial>(?:\.part|\.ytdl|\.temp)+)?$",
    re.IGNORECASE,
)


def section(title):
    print("\n" + "=" * 68)
    print("  " + title)
    print("=" * 68)


def collect_urls():
    section(t("c_step2"))
    print(t("c_paste"))
    print(t("c_more"))
    print(t("c_finish"))
    print(t("c_exit"))
    urls = []
    while True:
        label = t("c_link", n=len(urls) + 1)
        if urls:
            label += t("c_enter_download", n=len(urls))
        url = input(label + ": ").strip()
        if url.lower() in ("salir", "exit"):
            return []
        if not url:
            return urls
        if not url.startswith(("https://", "http://")):
            print(t("c_invalid_link"))
            continue
        if url in urls:
            print(t("c_duplicate"))
            continue
        urls.append(url)
        print(t("c_added", n=len(urls)))
        print(t("c_another"))


# ── File names ────────────────────────────────────────────────────────────
def is_social(url):
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in SOCIAL_DOMAINS)


def base_name(info):
    """YouTube and others: the video title. TikTok, Instagram and X: @username."""
    import yt_dlp

    key = (info.get("extractor_key") or "").lower()
    handle = None
    if key.startswith("tiktok"):
        handle = info.get("uploader") or info.get("channel")
    elif key.startswith("instagram"):
        handle = info.get("channel")
        if not handle:
            match = re.match(r"(?:Video|Post|Reel) by (.+)", info.get("title") or "")
            handle = match.group(1) if match else None
    elif key.startswith("twitter"):
        handle = info.get("uploader_id")
    elif key.startswith(("facebook", "threads")):
        handle = info.get("uploader")
    name = "@" + str(handle).strip().lstrip("@") if handle else (info.get("title") or info.get("id") or "video")
    name = shorten(yt_dlp.utils.sanitize_filename(str(name), restricted=False))
    return name or "video"


def shorten(name, limit=110):
    """Shortens long names at a whole word, without leaving stray punctuation at the end."""
    if len(name) > limit:
        cut = name[:limit]
        name = cut[:cut.rfind(" ")] if " " in cut[limit // 2:] else cut
    return name.rstrip(" .,;:-–—(¡¿[{").rstrip()


def clean_name(text):
    """Name typed by the user, without characters Windows does not allow."""
    import yt_dlp
    text = re.sub(r'[\\/:*?"<>|]+', "-", str(text)).strip()
    return yt_dlp.utils.sanitize_filename(text, restricted=False)[:120].rstrip(" .") or "video"


def choose_name(output, base, audio, reserved):
    """Returns a free name.

    First file with that name: "name". If another one arrives, the existing one becomes
    "name_01" and the new one is saved as "name_02", then "name_03"...
    The MP3 and the MP4 of the same video can share a name.
    """
    want = "audio" if audio else "video"
    occupied = set(reserved)
    finals = {}
    if output.exists():
        for path in output.iterdir():
            match = FILE_RE.match(path.name)
            if not match:
                continue
            stem = match["stem"].casefold()
            kind = "audio" if match["ext"].lower() == "mp3" else "video"
            if match["partial"] or kind == want:
                occupied.add(stem)
            if not match["partial"] and kind == want:
                finals.setdefault(stem, []).append((path, match.end("stem")))
    key = base.casefold()
    numbered = re.compile(re.escape(key) + r"_(\d+)$")
    numbers = [int(m.group(1)) for stem in occupied if (m := numbered.match(stem))]
    if key not in occupied and not numbers:
        return base
    if key in occupied:
        for path, stem_end in finals.get(key, []):
            target = path.with_name(path.name[:stem_end] + "_01" + path.name[stem_end:])
            if not target.exists():
                try:
                    path.rename(target)
                except OSError:
                    pass
        numbers.append(1)
    number = max(numbers) + 1
    while f"{key}_{number:02d}" in occupied:
        number += 1
    return f"{base}_{number:02d}"


class NameBook:
    """Remembers the name given to each video so a retry uses the same one."""

    def __init__(self):
        self.assigned = {}
        self.reserved = set()


# ── Download options ──────────────────────────────────────────────────────
def impersonation_available():
    try:
        import curl_cffi  # noqa: F401
        return True
    except Exception:
        return False


def make_options(output, quality, audio=False, names=None, incognito=False, custom_name=None):
    import yt_dlp

    names = names or NameBook()

    def assign_name(info, *, incomplete=False):
        if incomplete:
            return None
        identity = (info.get("extractor_key"), info.get("id"))
        if identity not in names.assigned:
            base = clean_name(custom_name) if custom_name else base_name(info)
            name = choose_name(output, base, audio, names.reserved)
            names.assigned[identity] = name
            names.reserved.add(name.casefold())
        info["videofetch_name"] = names.assigned[identity]
        return None

    # Quality is chosen by the short side of the picture, so it works the same for
    # horizontal (YouTube: 1280x720) and vertical videos (TikTok, Instagram: 720x1280).
    # "res:720" = the largest up to 720p; if the video has nothing that small,
    # the lowest quality available (it never fails for lack of a format).
    formats = "ba/b" if audio else "bv*+ba/b"
    resolution = {"720": "res:720", "1080": "res:1080"}.get(quality, "res")
    options = {
        "format": formats,
        # First the highest allowed resolution (720p, 1080p or the maximum) and, if tied,
        # H.264 + AAC (editor friendly). Resolution always wins.
        # If another format arrives, it is converted to H.264 + AAC at the end (see make_editor_fix).
        "format_sort": ["acodec:aac"] if audio else [resolution, "fps", "vcodec:h264", "acodec:aac"],
        "postprocessor_args": {"merger": ["-movflags", "+faststart"]},
        "outtmpl": str(output / "%(videofetch_name)s.%(ext)s"),
        "match_filter": assign_name,
        "windowsfilenames": True,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "continuedl": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "concurrent_fragment_downloads": 4,
        # Check the actual destination file instead of a permanent ID archive:
        # deleting a video must allow downloading it again.
        "overwrites": False,
        "remote_components": ["ejs:github"],
    }
    if audio:
        # MP3 with the video thumbnail as cover art.
        options["writethumbnail"] = True
        options["postprocessors"] = [
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"},
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
        ]
    if shutil.which("node"):
        options["js_runtimes"] = {"node": {}}
    if incognito:
        # "Incognito mode": no cache or stored cookies and, if curl_cffi is installed,
        # acting like a normal Chrome browser.
        options["cachedir"] = False
        options["sleep_interval_requests"] = 1
        if impersonation_available():
            from yt_dlp.networking.impersonate import ImpersonateTarget
            options["impersonate"] = ImpersonateTarget.from_str("chrome")
    return options


def probe_info(path):
    """Codecs, number of audio tracks and resolution of the file."""
    import json
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height", "-of", "json",
         str(path)], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    streams = json.loads(result.stdout or "{}").get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    first = videos[0] if videos else {}
    return {"video": first.get("codec_name"), "sound": audios[0].get("codec_name") if audios else None,
            "audios": len(audios), "width": first.get("width") or 0, "height": first.get("height") or 0}


VIDEO_ENCODERS = [
    # NVIDIA, Intel or AMD graphics card (much faster); otherwise, the CPU.
    ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-b:v", "0", "-pix_fmt", "yuv420p"]),
    ("h264_qsv", ["-c:v", "h264_qsv", "-global_quality", "20", "-pix_fmt", "nv12"]),
    ("h264_amf", ["-c:v", "h264_amf", "-quality", "quality", "-rc", "cqp", "-qp_i", "18", "-qp_p", "20", "-pix_fmt", "yuv420p"]),
    ("libx264", ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p"]),
]
_available_encoders = None


def video_encoders():
    global _available_encoders
    if _available_encoders is None:
        listing = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        _available_encoders = [(name, args) for name, args in VIDEO_ENCODERS if f" {name} " in listing]
    return _available_encoders


def media_duration(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                            capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def run_ffmpeg(command, duration, notify):
    """Runs FFmpeg reporting the percentage. Returns (ok, error message)."""
    process = subprocess.Popen(command + ["-progress", "pipe:1", "-nostats"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for line in process.stdout:
        if line.startswith("out_time_us=") and duration:
            try:
                notify("progress", min(99.0, int(line.split("=", 1)[1]) / 1_000_000 / duration * 100))
            except ValueError:
                pass
    error = process.stderr.read()
    return process.wait() == 0, error


def make_editor_fix(downloader, notify, quality="original"):
    """Last step: if the MP4 is not H.264 + AAC, converts it so video editors can read it."""
    from yt_dlp.postprocessor.common import PostProcessor

    class EditorCompat(PostProcessor):
        def run(self, info):
            path = info.get("filepath")
            if not path or not shutil.which("ffprobe"):
                return [], info
            path = Path(path)
            details = probe_info(path)
            video, sound = details["video"], details["sound"]
            if not video:
                return [], info
            self.report(info, details)
            # If the site only offered more quality than requested (e.g. a reel only in 1080p
            # when you chose 720p), it is scaled down so it takes the space you expect.
            wanted = {"720": 720, "1080": 1080}.get(quality)
            short = min(details["width"], details["height"])
            scale = []
            if wanted and short > wanted * 1.05:
                size = f"-2:{wanted}" if details["width"] >= details["height"] else f"{wanted}:-2"
                scale = ["-vf", f"scale={size}"]
                notify("log", t("reduced", short=short, wanted=wanted))
            fix_video = video != "h264" or bool(scale)
            fix_audio = sound not in (None, "aac")
            extra_audio = details["audios"] > 1
            is_mp4 = path.suffix.lower() == ".mp4"
            if is_mp4 and not fix_video and not fix_audio and not extra_audio:
                return [], info
            if extra_audio and not fix_video and not fix_audio and is_mp4:
                # Several audio tracks confuse editors: only the main one is kept.
                notify("log", t("audio_tracks", n=details["audios"]))
            notify("status", t("converting_status"))
            notify("log", t("converting_log", ext=path.suffix[1:], video=video, sound=sound or t("no_audio")))
            notify("progress", 0)
            target = path.with_suffix(".mp4")
            temporary = target.with_name(target.stem + ".convert.mp4")
            duration = media_duration(path)
            encoders = video_encoders() if fix_video else [("copy", ["-c:v", "copy"])]
            ok, error = False, ""
            for name, video_args in encoders:
                command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(path),
                           "-map", "0:v:0", "-map", "0:a:0?", *scale, *video_args]
                command += ["-c:a", "aac", "-b:a", "192k"] if fix_audio else ["-c:a", "copy"]
                command += ["-movflags", "+faststart", str(temporary)]
                ok, error = run_ffmpeg(command, duration, notify)
                if ok:
                    if fix_video:
                        notify("log", t("converted_with", name=name))
                    break
                temporary.unlink(missing_ok=True)
            if not ok:
                notify("log", t("convert_failed") + error.strip()[-300:])
                return [], info
            temporary.replace(target)
            if target != path:
                path.unlink(missing_ok=True)
                info["filepath"] = str(target)
                info["ext"] = "mp4"
            notify("progress", 100)
            return [], info

        def report(self, info, details):
            """Reports the real quality obtained and whether the site offers nothing better."""
            short = min(details["width"], details["height"]) or max(details["width"], details["height"])
            if not short:
                return
            notify("log", t("resolution", w=details["width"], h=details["height"], short=short))
            offered = [min(f.get("width") or 0, f.get("height") or 0) or (f.get("height") or 0)
                       for f in info.get("formats") or [] if (f.get("vcodec") or "none") != "none"]
            best = max(offered, default=0)
            wanted = {"720": 720, "1080": 1080}.get(quality, 100000)
            if short < min(wanted, 720) and (not best or best <= short):
                notify("note", t("max_offered", short=short))

    return EditorCompat(downloader)


BROWSERS = {"firefox": "Firefox", "chrome": "Chrome"}
def remove_leftovers(output, names):
    """Before retrying, deletes empty or partial leftovers from the failed attempt
    (e.g. "The downloaded file is empty"), so the retry starts clean."""
    for name in names.assigned.values():
        for path in output.glob(glob_escape(name) + ".*"):
            try:
                if path.name.endswith((".part", ".ytdl", ".temp")) or path.stat().st_size == 0:
                    path.unlink()
            except OSError:
                pass


def glob_escape(text):
    return re.sub(r"([*?\[])", r"[\1]", text)


def download(url, output, quality, audio=False, extra=None, notify=None, cancelled=lambda: False,
             browser=None, custom_name=None):
    """Downloads one link. Returns True if it finished correctly.

    1. Normal attempt.
    2. Social media: retry in incognito mode.
    3. If a browser was chosen: retry with your session (cookies) from that browser,
       for protected, age-restricted or members-only videos.
    """
    import yt_dlp

    notify = notify or (lambda kind, text="": None)
    names = NameBook()
    attempts = ["normal"]
    if is_social(url):
        attempts.append("incognito")
    if browser in BROWSERS:
        attempts.append("cookies")
    unsupported = False
    for mode in attempts:
        if cancelled():
            return False
        if mode == "incognito":
            notify("incognito", t("retry_incognito"))
            if not impersonation_available():
                notify("log", t("tip_update"))
        if mode == "cookies":
            if unsupported:
                break
            notify("incognito", t("retry_cookies", browser=BROWSERS[browser]))
        if mode != "normal":
            remove_leftovers(output, names)
        options = make_options(output, quality, audio, names, mode == "incognito", custom_name)
        if mode == "cookies":
            options["cookiesfrombrowser"] = (browser,)
        options.update(extra or {})
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                if not audio:
                    downloader.add_post_processor(make_editor_fix(downloader, notify, quality),
                                                  when="post_process")
                if not downloader.download([url]):
                    return True
        except Exception as exc:
            if cancelled():
                return False
            message = str(exc)
            if "Unsupported URL" in message:
                unsupported = True
            if "DRM" in message:
                notify("log", t("drm"))
                return False
            if mode == "cookies" and browser == "chrome" and (
                    "cookie" in message.lower() or "DPAPI" in message or "decrypt" in message.lower()):
                notify("log", t("chrome_locked", browser=BROWSERS[browser]))
            elif not isinstance(exc, yt_dlp.utils.DownloadError):
                notify("log", message)
    if unsupported:
        notify("log", t("unsupported"))
    return False


def main():
    if "--lang" in sys.argv[1:-1]:
        set_language(sys.argv[sys.argv.index("--lang") + 1])
    parser = argparse.ArgumentParser(description=t("c_description"))
    parser.add_argument("urls", nargs="*")
    parser.add_argument("--quality", choices=["720", "1080", "original"], default="original")
    parser.add_argument("--mp3", action="store_true", help=t("c_help_mp3"))
    parser.add_argument("--cookies", choices=sorted(BROWSERS), help=t("c_help_cookies"))
    parser.add_argument("--nombre", "--name", dest="nombre", help=t("c_help_name"))
    parser.add_argument("--lang", choices=LANGUAGES, help=t("c_help_lang"))
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.update:
        return subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(LIB),
                                "yt-dlp[default,curl-cffi]"])
    import yt_dlp
    if args.check:
        print(t("c_tool"), yt_dlp.version.__version__)
        for tool in ("ffmpeg", "ffprobe", "node"):
            print(tool + ":", shutil.which(tool) or t("c_not_found"))
        print(t("c_incognito"), t("c_yes") if impersonation_available() else t("c_no_update"))
        print(t("c_destination"), DOWNLOADS)
        return 0
    if not shutil.which("ffmpeg"):
        print(t("c_no_ffmpeg"))
        return 1
    urls = args.urls
    quality = args.quality
    audio = args.mp3
    if not urls:
        section(t("c_header"))
        print(t("c_saved_in"))
        section(t("c_step1"))
        for key in ("c_opt1", "c_opt2", "c_opt3", "c_opt4", "c_opt0"):
            print(t(key))
        while True:
            choice = input(t("c_choose")).strip()
            if choice == "0":
                return 0
            if choice == "4":
                quality, audio = "original", True
                break
            quality = {"": "original", "1": "720", "2": "1080", "3": "original"}.get(choice)
            if quality:
                break
            print(t("c_bad_option"))
        urls = collect_urls()
    if not urls:
        print(t("c_no_links"))
        return 0
    if any(not url.startswith(("https://", "http://")) for url in urls):
        print(t("c_full_links"))
        return 1
    output = DOWNLOADS
    output.mkdir(exist_ok=True)
    section(t("c_running"))
    print(t("c_in_list"), len(urls))
    if audio:
        print(t("c_format_mp3"))
    else:
        print(t("c_quality"), t("c_best") if quality == "original" else quality + "p")
    print(t("c_save_in"), output)
    print(t("c_ctrl_c"))
    failures = 0
    for index, url in enumerate(urls, 1):
        section(t("c_link_of", i=index, n=len(urls)))
        print("  " + url + "\n", flush=True)
        if not download(url, output, quality, audio, browser=args.cookies, custom_name=args.nombre,
                        notify=lambda kind, text="": kind != "progress" and print("  " + str(text))):
            failures += 1
    section(t("c_summary"))
    print(t("c_ok", n=len(urls) - failures))
    print(t("c_errors", n=failures))
    print(t("c_folder"), output)
    if failures:
        print(t("c_repeat"))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print(t("c_cancelled"))
