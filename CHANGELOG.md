# Changelog

**English** · [Español](CHANGELOG.es.md)

All notable changes to VideoFetch are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/).

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
