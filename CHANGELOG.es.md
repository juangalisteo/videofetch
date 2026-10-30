# Historial de versiones

[English](CHANGELOG.md) · **Español**

Todos los cambios importantes de VideoFetch se apuntan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y versiones según [Semantic Versioning](https://semver.org/lang/es/).

## [Sin publicar]

### Cambiado
- **Licencia cambiada de MIT a GPL-3.0 o posterior**, de acuerdo los dos autores.
  Las versiones 1.0.0 y 1.1.0 siguen disponibles con licencia MIT.
- `01_DESCARGAR.cmd` detecta la primera vez sin yt-dlp y ofrece instalarlo
  (antes la ventana no se abría y no avisaba hasta abrir `02_ACTUALIZAR.cmd`).
- Mensajes más claros cuando no hay enlaces o uno no es válido (dice cuál).
- Se aceptan enlaces pegados sin `https://` (`youtube.com/...`, `youtu.be/...`).

## [1.1.0] · 30-10-2026

### Añadido
- **Selector de idioma ES / EN** arriba, a la izquierda de la versión. Cambia toda la
  ventana al momento sin perder lo escrito (enlaces, formato, calidad, nombres y actividad).
- La primera vez usa el idioma de Windows; después recuerda la elección.
- Todos los textos (ventana, avisos, actividad y modo consola) en `APP/idiomas.py`.
- Modo consola en inglés con `--lang en` (y `--name` como alias de `--nombre`).
- Registro de errores de la ventana en `APP/videofetch_errores.log`.
- README, historial de versiones y guía rápida (`00_README_EN.txt`) en inglés.

### Cambiado
- Comentarios y descripciones del código traducidos al inglés (sin cambios en el código).

## [1.0.0] · 30-10-2026

Primera versión publicada.

### Añadido
- Ventana de escritorio (Tkinter) con diseño grafito y naranja `#FF5A1F`.
- Descarga de varios enlaces a la vez (uno por línea, sin repetidos).
- Formatos **MP4** y **MP3** (con carátula).
- Calidades **720p**, **1080p** y **Máxima**, también para vídeos verticales.
- MP4 siempre en **H.264 + AAC**, compatible con editores de vídeo; conversión
  con tarjeta gráfica (NVIDIA, Intel o AMD) cuando la hay.
- Nombres automáticos (título o `@usuario`), sin sobrescribir nunca (`_01`, `_02`…).
- Nombre propio opcional para cada enlace.
- Reintentos automáticos: modo incógnito y cookies de Firefox o Chrome.
- Avisos claros de DRM y webs no compatibles.
- Panel *Ver actividad* con progreso, resolución conseguida y botón *Detener*.
- Modo consola (`APP\descargador.py`).
- Accesos `01_DESCARGAR`, `02_ACTUALIZAR` y `03_CREAR_ACCESO_DIRECTO`.
