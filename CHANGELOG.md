# Changelog

**English** · [Español](CHANGELOG.es.md)

All notable changes to VideoFetch are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/).

## [1.2.0] · 2026-10-31

### Added
- **SRT subtitles button** next to the quality buttons (small; red when off, green when on,
  remembered). It saves `name.srt` next to the video, in the window's language:
  - first, the site's own subtitles (YouTube, including its automatic translation, and TikTok);
  - if the site has none (Instagram, X, TikTok without captions…), they are **created with AI
    (Whisper)** on your computer, using an NVIDIA card when available, and translated if needed.
- Console mode: `--srt`.
- `02_ACTUALIZAR.cmd` also installs the AI parts (faster-whisper, deep-translator) and saves
  its output to `APP/videofetch_actualizar.log`.

### Changed
- **License changed from MIT to GPL-3.0-or-later**, agreed by both authors.
  Versions 1.0.0 and 1.1.0 remain available under MIT.
- `01_DESCARGAR.cmd` detects a first run without yt-dlp and offers to install it
  (before, the window simply did not open until `02_ACTUALIZAR.cmd` was run).
- Clearer messages when there are no links or a link is not valid (it shows which one).
- The links box keeps a fixed height of 5 lines; extra lines scroll inside it and the
  line being typed is always visible. Hiding the activity shrinks the window back.
- The last quality chosen (720p / 1080p / Best) is remembered for the next time.
- Links pasted without `https://` (`youtube.com/...`, `youtu.be/...`) are accepted.

## [1.1.0] · 2026-10-30

### Added
- **ES / EN language selector** at the top, left of the version. It switches the whole
  window instantly without losing what you typed (links, format, quality, names and activity).
- On first launch it follows the Windows language; after that it remembers your choice.
- Every text (window, dialogs, activity and console mode) lives in `APP/idiomas.py`.
- English console mode with `--lang en` (and `--name` as an alias of `--nombre`).
- Window error log in `APP/videofetch_errores.log`.
- README, changelog and quick guide (`00_README_EN.txt`) in English.

### Changed
- Code comments and docstrings translated to English (no code changes).

## [1.0.0] · 2026-10-30

First public release.

### Added
- Desktop window (Tkinter) with a graphite and `#FF5A1F` orange design.
- Download several links at once (one per line, duplicates skipped).
- **MP4** and **MP3** formats (MP3 with cover art).
- **720p**, **1080p** and **Best** quality, vertical videos included.
- MP4 always in **H.264 + AAC**, compatible with video editors; conversion
  uses the graphics card (NVIDIA, Intel or AMD) when available.
- Automatic names (title or `@username`), never overwriting (`_01`, `_02`…).
- Optional custom name for each link.
- Automatic retries: incognito mode and Firefox or Chrome cookies.
- Clear warnings for DRM and unsupported sites.
- *Show activity* panel with progress, resolution obtained and a *Stop* button.
- Console mode (`APP\descargador.py`).
- `01_DESCARGAR`, `02_ACTUALIZAR` and `03_CREAR_ACCESO_DIRECTO` launchers.
