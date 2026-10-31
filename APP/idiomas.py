"""VideoFetch · application texts in Spanish and English.

Every text the user sees lives here. To change a sentence, change it only in
this file. t("key") returns the text in the chosen language.

Project:   VideoFetch v1.2.0
Authors:   Juan Bautista Galisteo Marqués (@juangalisteo)
           Juan Manuel Casado Triguero (@juanmacasado)
License:   GPL-3.0-or-later (see LICENSE)
Copyright (C) 2026 Juan Bautista Galisteo Marqués and Juan Manuel Casado Triguero.
This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License, version 3 or (at your option) any later version.
"""
import json
import locale
import sys
from pathlib import Path

LANGUAGES = ["es", "en"]
SETTINGS = Path(__file__).resolve().parent / "videofetch_ajustes.json"

TEXTS = {
    # ── Window: header and intro ──
    "subtitle": ("Descargador de vídeos", "Video downloader"),
    "title": ("Tus vídeos, en tu equipo", "Your videos, on your computer"),
    "lead": ("Guarda tus vídeos directamente en tu equipo, sin anuncios ni registros.",
             "Save your videos straight to your computer, with no ads and no sign-ups."),

    # ── 01 Links ──
    "links": ("Enlaces", "Links"),
    "links_hint": ("Un enlace por línea · Los repetidos se descargan una sola vez",
                   "One link per line · Duplicates are downloaded only once"),
    "placeholder": ("Pega aquí tus enlaces de YouTube, TikTok o Instagram",
                    "Paste your YouTube, TikTok or Instagram links here"),
    "videos": (("{n} vídeo", "{n} vídeos"), ("{n} video", "{n} videos")),
    "repeated": (("{n} repetido", "{n} repetidos"), ("{n} duplicate", "{n} duplicates")),

    # ── 02 Format and 03 Quality ──
    "format": ("Formato", "Format"),
    "format_mp4": ("MP4  Vídeo", "MP4  Video"),
    "format_mp3": ("MP3  Audio", "MP3  Audio"),
    "hint_mp4": ("Vídeo con audio", "Video with audio"),
    "hint_mp3": ("Solo audio", "Audio only"),
    "quality": ("Calidad", "Quality"),
    "quality_max": ("Máxima", "Best"),
    "hint_720": ("Hasta 720p · Ocupa menos espacio", "Up to 720p · Takes up less space"),
    "hint_1080": ("Hasta 1080p · Alta definición", "Up to 1080p · High definition"),
    "hint_max": ("La mejor calidad", "The best quality available"),
    "hint_quality_mp3": ("Audio en MP3", "MP3 audio"),
    "hint_srt": ("Con subtítulos .srt", "With .srt subtitles"),

    # ── 04 Name and 05 Destination ──
    "file_name": ("Nombre del archivo", "File name"),
    "destination": ("Destino", "Destination"),
    "open_folder": ("Abrir carpeta", "Open folder"),

    # ── Small line: cookies ──
    "cookies_firefox": ("Cookies de Firefox", "Firefox cookies"),
    "cookies_chrome": ("Cookies de Chrome", "Chrome cookies"),

    # ── Status, buttons and activity ──
    "ready": ("Todo listo · Añade tus enlaces para comenzar", "All set · Add your links to get started"),
    "show_activity": ("Ver actividad", "Show activity"),
    "hide_activity": ("Ocultar actividad", "Hide activity"),
    "download": ("Descargar", "Download"),
    "stop": ("Detener", "Stop"),
    "stopping": ("Deteniendo…", "Stopping…"),
    "downloading": ("Descargando {i} de {n}", "Downloading {i} of {n}"),
    "to_mp3": ("Convirtiendo a MP3…", "Converting to MP3…"),
    "merging": ("Uniendo vídeo y audio…", "Merging video and audio…"),
    "stopped_by_user": ("Descarga detenida por el usuario", "Download stopped by the user"),
    "warning": ("Aviso: ", "Warning: "),
    "quality_log": ("Calidad: ", "Quality: "),
    "downloaded": (("{n} descargado", "{n} descargados"), ("{n} downloaded", "{n} downloaded")),
    "with_error": ("{n} con error", "{n} failed"),
    "status_stopped": ("Detenido · {done}", "Stopped · {done}"),
    "status_failed": ("Terminado · {done} · {errors}. Mira la actividad para ver el motivo.",
                      "Finished · {done} · {errors}. Check the activity to see why."),
    "status_note": ("Listo · {done} · {note}", "Done · {done} · {note}"),
    "status_done": (("Listo · {done}. Ya está en la carpeta DOWNLOADS.",
                     "Listo · {done}. Ya están en la carpeta DOWNLOADS."),
                    ("Done · {done}. It's in the DOWNLOADS folder.",
                     "Done · {done}. They're in the DOWNLOADS folder.")),

    # ── Dialogs ──
    "no_links_title": ("Error", "Error"),
    "no_links": ("Pega el enlace de un vídeo para empezar.", "Paste a video link to get started."),
    "bad_link_title": ("Enlace no válido", "Invalid link"),
    "bad_link": ("Esto no parece el enlace de un vídeo:\n\n{link}\n\n"
                 "Copia la dirección completa del vídeo desde el navegador o la app y vuelve a pegarla.",
                 "This does not look like a video link:\n\n{link}\n\n"
                 "Copy the full video address from your browser or app and paste it again."),
    "no_ffmpeg_title": ("Falta FFmpeg", "FFmpeg is missing"),
    "no_ffmpeg": ("No se encuentra FFmpeg, necesario para unir y convertir el vídeo y el audio.",
                  "FFmpeg was not found. It is needed to merge and convert the video and audio."),
    "busy_title": ("Descarga en marcha", "Download in progress"),
    "busy": ("Pulsa Detener y espera a que termine antes de cerrar.",
             "Press Stop and wait for it to finish before closing."),

    # ── Downloader messages (activity) ──
    "reduced": ("La web solo ofrecía {short}p · Se reduce a {wanted}p como has pedido",
                "The site only offered {short}p · Scaled down to {wanted}p as you asked"),
    "audio_tracks": ("El vídeo traía {n} pistas de audio · Se deja solo la principal",
                     "The video had {n} audio tracks · Keeping only the main one"),
    "converting_status": ("Convirtiendo para editores de vídeo… puede tardar unos minutos",
                          "Converting for video editors… this may take a few minutes"),
    "converting_log": ("Convirtiendo a MP4 H.264 + AAC (era {ext} {video} + {sound})",
                       "Converting to MP4 H.264 + AAC (was {ext} {video} + {sound})"),
    "no_audio": ("sin audio", "no audio"),
    "converted_with": ("Convertido con {name}", "Converted with {name}"),
    "convert_failed": ("Aviso: no se pudo convertir para editores: ", "Warning: could not convert for editors: "),
    "resolution": ("Resolución descargada: {w}×{h} ({short}p)", "Downloaded resolution: {w}×{h} ({short}p)"),
    "max_offered": ("{short}p · Es lo máximo que ofrece esta web", "{short}p · That's the best this site offers"),
    "retry_incognito": ("Ha fallado. Reintentando en modo incógnito…", "It failed. Retrying in incognito mode…"),
    "tip_update": ("Consejo: abre 02_ACTUALIZAR.cmd una vez para que el modo incógnito pueda hacerse pasar "
                   "por un navegador real.",
                   "Tip: run 02_ACTUALIZAR.cmd once so incognito mode can act like a real browser."),
    "retry_cookies": ("Reintentando con tu sesión de {browser}…", "Retrying with your {browser} session…"),
    "drm": ("Esta web protege sus vídeos (DRM) · Busca el mismo vídeo en YouTube o redes sociales",
            "This site protects its videos (DRM) · Look for the same video on YouTube or social media"),
    "chrome_locked": ("{browser} no deja leer sus cookies mientras está abierto o las protege. "
                      "Ciérralo del todo y vuelve a probar, o elige Firefox.",
                      "{browser} won't share its cookies while it is open, or protects them. "
                      "Close it completely and try again, or choose Firefox."),
    "unsupported": ("Esta web no es compatible con VideoFetch.", "This site is not supported by VideoFetch."),

    # ── Subtitles (SRT button) ──
    "subs_from_site": ("Subtítulos de la web guardados: {file}", "Subtitles from the site saved: {file}"),
    "subs_with_ai": ("La web no da subtítulos · Se crean con IA (Whisper) en tu equipo",
                     "The site has no subtitles · Creating them with AI (Whisper) on your computer"),
    "subs_ai_status": ("Creando subtítulos con IA… puede tardar unos minutos",
                       "Creating subtitles with AI… this may take a few minutes"),
    "ai_model_download": ("Descargando el modelo de IA de subtítulos (solo la primera vez, unos 500 MB)…",
                          "Downloading the AI subtitle model (first time only, about 500 MB)…"),
    "subs_translating": ("Traduciendo los subtítulos…", "Translating the subtitles…"),
    "subs_ready": ("Subtítulos listos: {file}", "Subtitles ready: {file}"),
    "subs_no_speech": ("No se ha oído voz en el vídeo · No hay subtítulos que crear",
                       "No speech was heard in the video · No subtitles to create"),
    "subs_no_translation": ("Aviso: no se pudo traducir (¿sin Internet?) · Se guardan en el idioma original. ",
                            "Warning: could not translate (no Internet?) · Saved in the original language. "),
    "subs_failed": ("Aviso: no se pudieron crear los subtítulos: ", "Warning: could not create the subtitles: "),
    "ai_missing": ("Falta la pieza de subtítulos con IA · Abre 02_ACTUALIZAR.cmd una vez y vuelve a probar",
                   "The AI subtitle part is missing · Run 02_ACTUALIZAR.cmd once and try again"),

    # ── Console mode ──
    "c_step2": ("PASO 2 DE 2  |  AÑADIR VÍDEOS", "STEP 2 OF 2  |  ADD VIDEOS"),
    "c_paste": ("  Pega un enlace y pulsa ENTER para añadirlo.", "  Paste a link and press ENTER to add it."),
    "c_more": ("  Puedes seguir pegando más enlaces, uno por línea.", "  You can keep pasting more links, one per line."),
    "c_finish": ("  Cuando termines, pulsa ENTER SIN ESCRIBIR para descargar.",
                 "  When you are done, press ENTER WITHOUT TYPING to download."),
    "c_exit": ("  Escribe SALIR para cancelar.\n", "  Type EXIT to cancel.\n"),
    "c_exit_word": ("salir", "exit"),
    "c_link": ("  Enlace {n}", "  Link {n}"),
    "c_enter_download": (" [ENTER = descargar {n}]", " [ENTER = download {n}]"),
    "c_invalid_link": ("  ! Enlace no válido. Pega la dirección completa https://...\n",
                       "  ! Invalid link. Paste the full https://... address\n"),
    "c_duplicate": ("  ! Este enlace ya está en la lista.\n", "  ! This link is already in the list.\n"),
    "c_added": ("  OK - Enlace {n} añadido.", "  OK - Link {n} added."),
    "c_another": ("  >> Pega otro enlace o pulsa ENTER para EMPEZAR.\n",
                  "  >> Paste another link or press ENTER to START.\n"),
    "c_description": ("Descarga vídeos dentro de esta carpeta de herramientas.",
                      "Downloads videos into this tool folder."),
    "c_help_mp3": ("Guardar solo el audio en MP3", "Save only the audio as MP3"),
    "c_help_cookies": ("Usar la sesión de este navegador si hace falta", "Use this browser's session if needed"),
    "c_help_name": ("Nombre para los archivos (opcional)", "Name for the files (optional)"),
    "c_help_lang": ("Idioma: es o en", "Language: es or en"),
    "c_help_srt": ("Guardar también los subtítulos .srt (de la web o creados con IA)",
                   "Also save .srt subtitles (from the site or created with AI)"),
    "c_tool": ("Herramienta:", "Tool:"),
    "c_not_found": ("NO ENCONTRADO", "NOT FOUND"),
    "c_incognito": ("Modo incógnito completo:", "Full incognito mode:"),
    "c_yes": ("SÍ", "YES"),
    "c_no_update": ("NO (abre 02_ACTUALIZAR.cmd)", "NO (run 02_ACTUALIZAR.cmd)"),
    "c_destination": ("Destino:", "Destination:"),
    "c_no_ffmpeg": ("Falta FFmpeg. Es necesario para unir el vídeo y el audio.",
                    "FFmpeg is missing. It is needed to merge the video and audio."),
    "c_header": ("VIDEOFETCH  |  Tus vídeos, en tu equipo", "VIDEOFETCH  |  Your videos, on your computer"),
    "c_saved_in": ("  Las descargas se guardan dentro de VIDEOFETCH / DOWNLOADS.",
                   "  Downloads are saved inside VIDEOFETCH / DOWNLOADS."),
    "c_step1": ("PASO 1 DE 2  |  ELEGIR CALIDAD", "STEP 1 OF 2  |  CHOOSE QUALITY"),
    "c_opt1": ("  [1]  Vídeo hasta 720p          Menor espacio", "  [1]  Video up to 720p          Less space"),
    "c_opt2": ("  [2]  Vídeo hasta 1080p         Mayor detalle, más espacio",
               "  [2]  Video up to 1080p         More detail, more space"),
    "c_opt3": ("  [3]  Vídeo mejor disponible   Conserva la resolución disponible",
               "  [3]  Best video available     Keeps the available resolution"),
    "c_opt4": ("  [4]  Solo audio MP3            Saca el sonido del vídeo",
               "  [4]  MP3 audio only            Takes the sound from the video"),
    "c_opt0": ("  [0]  Salir\n", "  [0]  Exit\n"),
    "c_choose": ("  Elige 1, 2, 3 o 4 [ENTER = mejor disponible]: ", "  Choose 1, 2, 3 or 4 [ENTER = best available]: "),
    "c_bad_option": ("  ! Opción no válida. Elige 1, 2, 3, 4 o 0.", "  ! Invalid option. Choose 1, 2, 3, 4 or 0."),
    "c_no_links": ("No has indicado enlaces.", "You did not give any links."),
    "c_full_links": ("Utiliza enlaces completos que empiecen por https:// o http://.",
                     "Use full links that start with https:// or http://."),
    "c_running": ("DESCARGA EN MARCHA", "DOWNLOAD IN PROGRESS"),
    "c_in_list": ("  Enlaces en la lista:", "  Links in the list:"),
    "c_format_mp3": ("  Formato: MP3 (solo audio)", "  Format: MP3 (audio only)"),
    "c_quality": ("  Calidad:", "  Quality:"),
    "c_best": ("Mejor disponible", "Best available"),
    "c_save_in": ("  Guardar en:", "  Save to:"),
    "c_ctrl_c": ("  CTRL+C = detener.", "  CTRL+C = stop."),
    "c_link_of": ("ENLACE {i} DE {n}", "LINK {i} OF {n}"),
    "c_summary": ("RESUMEN FINAL", "FINAL SUMMARY"),
    "c_ok": ("  Descargados sin error: {n}", "  Downloaded without errors: {n}"),
    "c_errors": ("  Con error:             {n}", "  Failed:                     {n}"),
    "c_folder": ("  Carpeta:              ", "  Folder:                     "),
    "c_repeat": ("  Repite los enlaces con error para reintentar.", "  Run the failed links again to retry."),
    "c_cancelled": ("\nCancelado. Puedes repetir los mismos enlaces cuando quieras.",
                    "\nCancelled. You can run the same links again whenever you want."),
}

_current = None


def system_language():
    """Spanish if Windows (or the system) is in Spanish; otherwise English."""
    try:
        if sys.platform == "win32":
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x0A:
                return "es"
            return "en"
    except Exception:
        pass
    try:
        name = (locale.getlocale()[0] or "").lower()
        return "es" if name.startswith(("es", "spanish")) else "en"
    except Exception:
        return "en"


def saved_language():
    try:
        value = json.loads(SETTINGS.read_text(encoding="utf-8")).get("language")
        return value if value in LANGUAGES else None
    except Exception:
        return None


def get_language():
    global _current
    if _current is None:
        _current = saved_language() or system_language()
    return _current


def set_language(code):
    global _current
    if code in LANGUAGES:
        _current = code


def t(key, n=None, **values):
    """Text in the current language. With n, picks singular or plural."""
    text = TEXTS[key][LANGUAGES.index(get_language())]
    if isinstance(text, tuple):
        text = text[0] if n == 1 else text[1]
    if n is not None:
        values["n"] = n
    return text.format(**values) if values else text
