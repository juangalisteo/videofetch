VIDEOFETCH v1.1.0 - VIDEO DOWNLOADER
(Espanol: lee 00_LEEME.txt)

HOW TO USE IT
1. Copy the WHOLE VIDEOFETCH folder wherever you like.
2. The first time, run 02_ACTUALIZAR.cmd once (it installs yt-dlp).
3. Double-click 01_DESCARGAR.cmd to open the window.
4. Paste one full link per line in the links box. Inside the box, on the
   right: clipboard icon = paste, bin icon = clear.
5. Choose the format: MP4 (video with audio) or MP3 (audio only).
6. For MP4 choose the quality: 720p, 1080p or Best.
7. Press Download (or Ctrl + Enter). You can show the activity and press Stop.
8. The Open folder button shows what you downloaded.

LANGUAGE
At the top right, next to the version, there are the ES / EN buttons.
They switch the whole window to Spanish or English instantly, without losing
what you typed. On first launch it follows the Windows language and then
remembers your choice.
In the console: APP\descargador.py --lang en

DESKTOP SHORTCUT
Double-click 03_CREAR_ACCESO_DIRECTO.cmd ONCE and VideoFetch will appear on
your desktop with its icon. If you move the folder, run it again.

The launcher files keep their Spanish names: DESCARGAR = download,
ACTUALIZAR = update, CREAR_ACCESO_DIRECTO = create shortcut, SISTEMA = system.

FOLDER STRUCTURE
VIDEOFETCH
  00_LEEME.txt                  Quick guide in Spanish
  00_README_EN.txt              This guide
  01_DESCARGAR.cmd              Opens VideoFetch
  02_ACTUALIZAR.cmd             Updates the download tool
  03_CREAR_ACCESO_DIRECTO.cmd   Creates the desktop shortcut
  DOWNLOADS\                    Your videos and audio files
  APP\                          The program: code, texts, icon and saved settings
  SISTEMA\                      Internal parts (yt-dlp and others). Do not touch.

DESTINATION
Files are saved in DOWNLOADS, INSIDE VIDEOFETCH.

FILE NAMES
- YouTube and other sites: the video title.   Example: My video.mp4
- TikTok, Instagram and X: the @username.     Example: @username.mp4
- If you download another video with the same name, the first one becomes
  @username_01.mp4 and the new ones @username_02.mp4, @username_03.mp4...
- The MP3 and MP4 of the same video can share a name.
- It never overwrites an existing file.
- CUSTOM NAME (optional), in "04 - File name": one box per link, in the same
  order you pasted them. Empty box = automatic name. The small x clears it.

READY FOR VIDEO EDITORS (Sony Vegas, Premiere, DaVinci...)
- Videos are always saved as MP4 with H.264 video and AAC audio.
- 720p and 1080p: downloaded directly in H.264 + AAC (fast and small).
- Best: downloads the highest quality available (4K if the video has it) and
  then converts it to H.264 + AAC. It takes longer; you will see "Converting
  for video editors" with a percentage. It uses your NVIDIA, Intel or AMD
  graphics card when available.
- MP3 files include the video thumbnail as cover art.

SOCIAL MEDIA AND INCOGNITO MODE
- If a TikTok, Instagram, X or Facebook video fails, VideoFetch retries it in
  "incognito mode": no stored data, acting like a normal Chrome browser.

BROWSER COOKIES (automatic)
- Every video is tried first WITHOUT cookies.
- If it fails (age-restricted, members only, live streams that just ended,
  "The downloaded file is empty"...), it retries with your session from the
  browser chosen at the bottom of the card: Firefox or Chrome.
- Recommended: Firefox. Chrome must be fully closed before downloading.
- It never stores or sends your passwords.

SUPPORTED SITES
- YouTube, TikTok, Instagram, X, Facebook, Vimeo, Twitch and many more.
- If a site is not supported or protects its videos (DRM), the activity
  will tell you.

REQUIREMENTS
Python, FFmpeg and Node.js installed and available on the PATH.
If the window ever hits an error, it is written to APP\videofetch_errores.log.
If YouTube changes something or an error appears, run 02_ACTUALIZAR.cmd.
It does not bypass DRM or access restrictions.

AUTHORS
Juan Bautista Galisteo Marques (github.com/juangalisteo) - author and lead
Juan Manuel Casado Triguero (github.com/juanmacasado) - collaborator
GPL-3.0 license (LICENSE file).
