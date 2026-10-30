# Historial de versiones

Todos los cambios importantes de VideoFetch se apuntan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y versiones según [Semantic Versioning](https://semver.org/lang/es/).

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
