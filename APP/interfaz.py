"""VideoFetch · ventana de descarga (comparte las opciones del lanzador de consola).

Proyecto:  VideoFetch v1.0.0
Autores:   Juan Bautista Galisteo Marqués (@juangalisteo)
           Juan Manuel Casado Triguero (@juanmacasado)
Licencia:  MIT (ver LICENSE)
"""
import importlib.util
import os
import queue
import re
import shutil
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox

sys.dont_write_bytecode = True  # sin carpetas __pycache__ junto al programa
APP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("descargador", APP / "descargador.py")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
ROOT, DOWNLOADS = core.ROOT, core.DOWNLOADS
import yt_dlp

APP_VERSION = "1.0.0"

# Texto nítido en pantallas con escalado (Windows).
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    try:
        # Para que la barra de tareas muestre el icono de VideoFetch y no el de Python.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VideoFetch.App")
    except Exception:
        pass

# ── Paleta: grafito monocromo con un único color de señal ────────────────
BG = "#0B0B0C"
SURFACE = "#121214"
FIELD = "#18181B"
RAISED = "#202024"
BORDER = "#26262B"
BORDER_STRONG = "#3A3A41"
TEXT = "#F4F4F5"
MUTED = "#A1A1AA"
FAINT = "#5E5E66"
ACCENT = "#FF5A1F"
ACCENT_SOFT = "#3A1A0E"
ACCENT_PRESS = "#E04A12"
ACCENT_HOVER = "#FF7A45"
SUCCESS = "#34D399"
WARNING = "#FBBF24"
DANGER = "#F87171"

SCALE = 1.0
UI_ZOOM = 0.8
F = {}


def px(value):
    return int(round(value * SCALE))


def pick_family(*names):
    available = set(tkfont.families())
    for name in names:
        if name in available:
            return name
    return "TkDefaultFont"


def setup_fonts(root):
    global SCALE
    # Toda la ventana un 20 % más pequeña (letras, botones y espacios).
    root.tk.call("tk", "scaling", float(root.tk.call("tk", "scaling")) * UI_ZOOM)
    SCALE = root.winfo_fpixels("1i") / 96
    ui = pick_family("Segoe UI Variable Text", "Segoe UI", "Inter", "DejaVu Sans")
    display = pick_family("Segoe UI Variable Display", "Segoe UI", "Inter Display", "Inter", "DejaVu Sans")
    semi = pick_family("Segoe UI Semibold", "Segoe UI Variable Text Semibold", "Inter SemiBold")
    mono = pick_family("Cascadia Mono", "Consolas", "DejaVu Sans Mono")

    def strong(size):
        if semi != "TkDefaultFont":
            return tkfont.Font(root, family=semi, size=size)
        return tkfont.Font(root, family=ui, size=size, weight="bold")

    F["title"] = tkfont.Font(root, family=display, size=28, weight="bold")
    F["lead"] = tkfont.Font(root, family=ui, size=11)
    F["body"] = tkfont.Font(root, family=ui, size=10)
    F["input"] = tkfont.Font(root, family=ui, size=11)
    F["small"] = tkfont.Font(root, family=ui, size=9)
    F["brand"] = strong(12)
    F["button"] = strong(10)
    F["chip"] = strong(9)
    F["tiny"] = tkfont.Font(root, family=ui, size=8)
    F["mono"] = tkfont.Font(root, family=mono, size=9)
    F["eyebrow"] = tkfont.Font(root, family=mono, size=8)


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r,
        x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


# ── Componentes ───────────────────────────────────────────────────────────
class Button(tk.Canvas):
    """Botón plano con esquinas redondeadas, hover y estado desactivado."""

    KINDS = {
        # El botón principal es naranja; los demás solo se aclaran al pasar el ratón.
        "primary": dict(bg=ACCENT, hover=ACCENT_HOVER, press=ACCENT_PRESS, fg=BG, fg_hover=BG,
                        border=None, off_bg="#1C1C20", off_fg="#55555C"),
        "secondary": dict(bg=FIELD, hover=RAISED, press="#2A2A2F", fg=TEXT, fg_hover=TEXT,
                          border=BORDER, off_bg=FIELD, off_fg=FAINT),
        "ghost": dict(bg=None, hover=FIELD, press=RAISED, fg=MUTED, fg_hover=TEXT,
                      border=None, off_bg=None, off_fg=FAINT),
    }

    def __init__(self, parent, text, command, kind="secondary", height=40, padx=18):
        self.parent_bg = parent["bg"]
        super().__init__(parent, bg=self.parent_bg, highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command, self.kind = text, command, self.KINDS[kind]
        self.h, self.padx = px(height), px(padx)
        self.state, self.hover, self.pressed = "normal", False, False
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, pressed=False))
        self.bind("<ButtonPress-1>", lambda e: self._set(pressed=True))
        self.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _set(self, **values):
        for key, value in values.items():
            setattr(self, key, value)
        self._draw()

    def _release(self, event):
        fire = self.pressed and self.hover and self.state == "normal"
        self._set(pressed=False)
        if fire and self.command:
            self.command()

    def _draw(self):
        k = self.kind
        self.delete("all")
        w = F["button"].measure(self.text) + 2 * self.padx
        tk.Canvas.configure(self, width=w, height=self.h)
        if self.state == "disabled":
            bg, fg = k["off_bg"], k["off_fg"]
        elif self.pressed and self.hover:
            bg, fg = k["press"], k.get("fg_hover", k["fg"])
        elif self.hover:
            bg, fg = k["hover"], k.get("fg_hover", k["fg"])
        else:
            bg, fg = k["bg"], k["fg"]
        bg = bg or self.parent_bg
        outline = k["border"] if k["border"] and self.state != "disabled" and not self.hover else bg
        rounded_rect(self, 1, 1, w - 1, self.h - 1, px(9), fill=bg, outline=outline)
        self.create_text(w / 2, self.h / 2, text=self.text, fill=fg, font=F["button"])

    def configure(self, **kw):
        redraw = False
        if "text" in kw:
            self.text = kw.pop("text")
            redraw = True
        if "state" in kw:
            self.state = kw.pop("state")
            tk.Canvas.configure(self, cursor="hand2" if self.state == "normal" else "arrow")
            redraw = True
        if kw:
            tk.Canvas.configure(self, **kw)
        if redraw:
            self._draw()

    config = configure


class Panel(tk.Canvas):
    """Contenedor con fondo redondeado y borde fino. Los hijos van en .inner."""

    def __init__(self, parent, bg=SURFACE, border=BORDER, radius=16, pad=24):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0, width=1, height=1)
        self.fill, self.border, self.radius, self.pad = bg, border, px(radius), px(pad)
        self.inner = tk.Frame(self, bg=bg)
        self.window = self.create_window(self.pad, self.pad, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._redraw)
        self.inner.bind("<Configure>", self._fit)
        self.after_idle(self._fit)

    def _fit(self, event=None):
        tk.Canvas.configure(self, height=self.inner.winfo_reqheight() + 2 * self.pad)

    def _redraw(self, event):
        self.delete("shape")
        rounded_rect(self, 1, 1, event.width - 1, event.height - 1, self.radius,
                     fill=self.fill, outline=self.border, tags="shape")
        self.tag_lower("shape")
        self.itemconfigure(self.window, width=max(1, event.width - 2 * self.pad),
                           height=max(1, event.height - 2 * self.pad))

    def set_border(self, color):
        self.itemconfigure("shape", outline=color)


class Chip(tk.Canvas):
    """Etiqueta en forma de píldora."""

    def __init__(self, parent, text, fg=MUTED, bg=None, border=BORDER, font=None):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0)
        self.fg, self.fill, self.border = fg, bg or parent["bg"], border
        self.font = font or F["chip"]
        self.set_text(text)

    def set_text(self, text, fg=None):
        self.fg = fg or self.fg
        self.delete("all")
        w, h = self.font.measure(text) + px(22), px(26)
        tk.Canvas.configure(self, width=w, height=h)
        rounded_rect(self, 1, 1, w - 1, h - 1, h / 2, fill=self.fill, outline=self.border)
        self.create_text(w / 2, h / 2, text=text, fill=self.fg, font=self.font)


class Segmented(tk.Canvas):
    """Selector segmentado: la opción elegida queda en blanco sobre negro."""

    def __init__(self, parent, options, index=0, command=None, min_width=0, compact=False):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0, cursor="hand2")
        self.options, self.index, self.command = options, index, command
        self.state, self.hovered = "normal", None
        self.font = F["tiny"] if compact else F["button"]
        self.inset, self.h = (px(2), px(22)) if compact else (px(4), px(40))
        self.radius = px(8) if compact else px(11)
        # Todas las opciones con el mismo ancho, para que el espacio entre ellas sea igual.
        widest = max(self.font.measure(o) for o in options) + (px(20) if compact else px(34))
        widths = [widest] * len(options)
        extra = max(0, px(min_width) - sum(widths) - 2 * self.inset)
        self.widths = [w + extra / len(widths) for w in widths]
        self.w = sum(self.widths) + 2 * self.inset
        tk.Canvas.configure(self, width=self.w, height=self.h)
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", lambda e: self._hover(None))
        self.bind("<Button-1>", self._click)
        self._draw()

    def _hit(self, x):
        left = self.inset
        for i, width in enumerate(self.widths):
            if left <= x < left + width:
                return i
            left += width
        return None

    def _hover(self, index):
        if index != self.hovered:
            self.hovered = index
            self._draw()

    def _motion(self, event):
        self._hover(self._hit(event.x) if self.state == "normal" else None)

    def _click(self, event):
        index = self._hit(event.x)
        if self.state == "normal" and index is not None and index != self.index:
            self.index = index
            self._draw()
            if self.command:
                self.command(index)

    def _draw(self):
        self.delete("all")
        off = self.state == "disabled"
        rounded_rect(self, 1, 1, self.w - 1, self.h - 1, self.radius, fill=FIELD, outline=BORDER)
        left = self.inset
        for i, (text, width) in enumerate(zip(self.options, self.widths)):
            if i == self.index:
                rounded_rect(self, left, self.inset, left + width, self.h - self.inset, self.radius - px(3),
                             fill=RAISED if off else ACCENT, outline=RAISED if off else ACCENT)
                color = FAINT if off else BG
            else:
                color = FAINT if off else (TEXT if i == self.hovered else MUTED)
            self.create_text(left + width / 2, self.h / 2, text=text, fill=color, font=self.font)
            left += width

    def current(self):
        return self.index

    def configure(self, **kw):
        if "state" in kw:
            self.state = "disabled" if kw.pop("state") == "disabled" else "normal"
            tk.Canvas.configure(self, cursor="hand2" if self.state == "normal" else "arrow")
            self.hovered = None
            self._draw()
        if kw:
            tk.Canvas.configure(self, **kw)

    config = configure


class ScrollArea(tk.Frame):
    """Zona con desplazamiento: si la pantalla es baja, nada se corta.
    Rueda del ratón para bajar y una barra fina a la derecha (solo aparece si hace falta)."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.bar = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0, width=px(10))
        self.content = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.span = (0.0, 1.0)
        self.grab = None
        self.canvas.configure(yscrollcommand=self._on_scroll)
        self.canvas.bind("<Configure>", self._resize)
        self.content.bind("<Configure>", self._resize)
        self.bar.bind("<Configure>", lambda e: self._draw_bar())
        self.bar.bind("<Button-1>", self._press)
        self.bar.bind("<B1-Motion>", self._drag)
        self.bar.bind("<ButtonRelease-1>", lambda e: setattr(self, "grab", None))
        self.after(300, self.watch)
        self.bind_all("<MouseWheel>", self._wheel, add="+")
        self.bind_all("<Button-4>", lambda e: self._wheel(e, -1), add="+")
        self.bind_all("<Button-5>", lambda e: self._wheel(e, 1), add="+")

    def needed_height(self):
        return self.content.winfo_reqheight()

    def watch(self):
        """Si el contenido cambia de alto (más casillas, actividad...), se reajusta solo."""
        needed = self.needed_height()
        if needed != getattr(self, "last_needed", None):
            self.last_needed = needed
            self._resize()
        self.after(150, self.watch)

    def _resize(self, event=None):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.itemconfigure(self.window, width=width, height=max(height, self.needed_height()))
        self.canvas.configure(scrollregion=(0, 0, width, max(height, self.needed_height())))

    def _on_scroll(self, first, last):
        self.span = (float(first), float(last))
        if self.span[0] <= 0 and self.span[1] >= 1:
            self.bar.pack_forget()
        elif not self.bar.winfo_manager():
            self.bar.pack(side="right", fill="y", before=self.canvas)
        self._draw_bar()

    def _draw_bar(self):
        self.bar.delete("all")
        h, w = self.bar.winfo_height(), px(10)
        top, bottom = self.span[0] * h, self.span[1] * h
        rounded_rect(self.bar, px(3), top + px(4), w - px(3), max(top + px(24), bottom - px(4)), px(3),
                     fill=BORDER_STRONG, outline=BORDER_STRONG)

    def _press(self, event):
        h = max(1, self.bar.winfo_height())
        top, bottom = self.span[0] * h, self.span[1] * h
        self.grab = event.y - top if top <= event.y <= bottom else (bottom - top) / 2
        self._drag(event)

    def _drag(self, event):
        h = max(1, self.bar.winfo_height())
        self.canvas.yview_moveto((event.y - (self.grab or 0)) / h)

    def _wheel(self, event, step=None):
        if step is None:
            step = -1 if event.delta > 0 else 1
        widget = event.widget
        while isinstance(widget, tk.Misc):
            target = getattr(widget, "wheel_target", None)
            if target is not None:
                target.yview_scroll(step, "units")
                return
            widget = widget.master
        if isinstance(event.widget, tk.Text) or self.span == (0.0, 1.0):
            return
        self.canvas.yview_scroll(step * 3, "units")


class SlimScrollbar(tk.Canvas):
    """Barra fina para subir y bajar dentro de un cuadro de texto.
    Aparece sola cuando hay más líneas de las que caben. Se puede arrastrar o hacer clic."""

    def __init__(self, parent, target):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0, width=px(12), height=1,
                         cursor="hand2")
        self.target, self.span, self.grab, self.hover = target, (0.0, 1.0), None, False
        target.configure(yscrollcommand=self.set)
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", lambda e: setattr(self, "grab", None))

    def set(self, first, last):
        self.span = (float(first), float(last))
        if self.span[0] <= 0 and self.span[1] >= 1:
            if self.winfo_manager():
                self.pack_forget()
        elif not self.winfo_manager():
            self.pack(side="right", fill="y", padx=(0, px(4)), pady=px(6), before=self.target)
        self._draw()

    def _hover(self, value):
        self.hover = value
        self._draw()

    def _draw(self):
        self.delete("all")
        h, w = self.winfo_height(), px(12)
        top, bottom = self.span[0] * h, self.span[1] * h
        color = ACCENT if self.hover or self.grab is not None else BORDER_STRONG
        rounded_rect(self, px(3), top + px(2), w - px(3), max(top + px(20), bottom - px(2)), px(3),
                     fill=color, outline=color)

    def _press(self, event):
        h = max(1, self.winfo_height())
        top, bottom = self.span[0] * h, self.span[1] * h
        # Clic en la barra: se arrastra. Clic fuera: salta a ese punto.
        self.grab = event.y - top if top <= event.y <= bottom else (bottom - top) / 2
        self._drag(event)

    def _drag(self, event):
        h = max(1, self.winfo_height())
        self.target.yview_moveto((event.y - (self.grab or 0)) / h)
        self._draw()


class NameField(tk.Frame):
    """Casilla de nombre (texto en naranja) con una × pequeña para borrarla."""

    def __init__(self, parent, variable, on_return):
        super().__init__(parent, bg=parent["bg"])
        self.variable = variable
        self.panel = Panel(self, bg=FIELD, border=BORDER, radius=10, pad=3)
        self.panel.pack(fill="x")
        row = tk.Frame(self.panel.inner, bg=FIELD)
        row.pack(fill="x")
        self.entry = tk.Entry(row, textvariable=variable, font=F["input"], bg=FIELD, fg=ACCENT,
                              disabledbackground=FIELD, disabledforeground=ACCENT_PRESS,
                              insertbackground=ACCENT, insertwidth=px(2), relief="flat", bd=0,
                              highlightthickness=0, selectbackground=ACCENT_SOFT, selectforeground=TEXT)
        self.entry.pack(side="left", fill="x", expand=True, padx=(px(8), 0), pady=px(4))
        self.clear = tk.Label(row, text="×", width=2, font=F["brand"], fg=FAINT, bg=FIELD, cursor="hand2")
        self.clear.pack(side="right", padx=(px(2), px(4)))
        self.clear.bind("<Enter>", lambda e: self.clear.configure(fg=ACCENT))
        self.clear.bind("<Leave>", lambda e: self.clear.configure(fg=FAINT))
        self.clear.bind("<Button-1>", self._clear)
        self.entry.bind("<FocusIn>", lambda e: self.panel.set_border(ACCENT))
        self.entry.bind("<FocusOut>", lambda e: self.panel.set_border(BORDER))
        self.entry.bind("<Return>", on_return)
        self.trace = variable.trace_add("write", lambda *a: self._refresh())
        self.bind("<Destroy>", self._forget, add="+")
        self._refresh()

    def _forget(self, event):
        # Al rehacer la lista, la casilla vieja deja de escuchar los cambios del nombre.
        if event.widget is self and self.trace:
            try:
                self.variable.trace_remove("write", self.trace)
            except tk.TclError:
                pass
            self.trace = None

    def _refresh(self):
        # La × solo se ve cuando hay algo escrito.
        self.clear.configure(text="×" if self.variable.get() else "")

    def _clear(self, event=None):
        if str(self.entry["state"]) == "normal":
            self.variable.set("")
            self.entry.focus_set()

    def set_state(self, state):
        self.entry.configure(state=state)
        self.clear.configure(cursor="hand2" if state == "normal" else "arrow")


class IconButton(tk.Canvas):
    """Botón diminuto sin texto, dibujado: "copy" (dos hojas), "paste" (portapapeles)
    o "clear" (papelera). Gris; naranja al pasar el ratón; ✓ verde un momento al pulsar."""

    def __init__(self, parent, kind, command, confirm=True):
        size = px(18)
        super().__init__(parent, width=size, height=size, bg=parent["bg"], highlightthickness=0, bd=0,
                         cursor="hand2")
        self.kind, self.command, self.confirm = kind, command, confirm
        self.size, self.color, self.done, self.state = size, FAINT, False, "normal"
        self.bind("<Enter>", lambda e: self._paint(ACCENT if self.state == "normal" else FAINT))
        self.bind("<Leave>", lambda e: self._paint(FAINT))
        self.bind("<Button-1>", self._click)
        self._draw()

    def _paint(self, color):
        self.color = color
        self._draw()

    def _draw(self):
        self.delete("all")
        s, w = self.size, max(1, px(1.4))
        color = self.color if self.state == "normal" else BORDER_STRONG
        if self.done:
            self.create_line(s * .2, s * .55, s * .42, s * .76, s * .82, s * .28, fill=SUCCESS, width=px(2))
        elif self.kind == "copy":
            self.create_rectangle(s * .35, s * .15, s * .85, s * .65, outline=color, width=w)
            self.create_rectangle(s * .15, s * .35, s * .65, s * .85, outline=color, width=w, fill=self["bg"])
        elif self.kind == "paste":
            self.create_rectangle(s * .2, s * .22, s * .8, s * .88, outline=color, width=w)
            self.create_rectangle(s * .36, s * .1, s * .64, s * .3, outline=color, width=w, fill=self["bg"])
            self.create_line(s * .34, s * .5, s * .66, s * .5, fill=color, width=w)
            self.create_line(s * .34, s * .68, s * .58, s * .68, fill=color, width=w)
        elif self.kind == "clear":
            self.create_line(s * .15, s * .27, s * .85, s * .27, fill=color, width=w)
            self.create_line(s * .4, s * .27, s * .4, s * .15, s * .6, s * .15, s * .6, s * .27, fill=color, width=w)
            self.create_polygon(s * .25, s * .33, s * .75, s * .33, s * .7, s * .88, s * .3, s * .88,
                                outline=color, fill="", width=w)
            self.create_line(s * .43, s * .45, s * .43, s * .76, fill=color, width=w)
            self.create_line(s * .57, s * .45, s * .57, s * .76, fill=color, width=w)

    def _click(self, event):
        if self.state != "normal":
            return
        self.command()
        if self.confirm:
            self.done = True
            self._draw()
            self.after(1200, self._reset)

    def _reset(self):
        self.done = False
        self._draw()

    def set_state(self, state):
        self.state = state
        self.configure(cursor="hand2" if state == "normal" else "arrow")
        self._draw()


def short_link(url, size=30):
    text = re.sub(r"^https?://(www\.)?", "", url)
    return text if len(text) <= size else text[:size - 1] + "…"


class Progress(tk.Canvas):
    """Barra de progreso fina."""

    def __init__(self, parent):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0, height=px(4), width=1)
        self.value, self.color = 0, ACCENT
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, value, color=None):
        self.value = max(0, min(100, value))
        self.color = color or self.color
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), px(4)
        rounded_rect(self, 0, 0, w, h, h / 2, fill=FIELD, outline=FIELD)
        filled = w * self.value / 100
        if filled >= h:
            rounded_rect(self, 0, 0, filled, h, h / 2, fill=self.color, outline=self.color)


def make_logo(parent):
    size = px(38)
    c = tk.Canvas(parent, width=size, height=size, bg=parent["bg"], highlightthickness=0, bd=0)
    rounded_rect(c, 0, 0, size, size, px(10), fill=ACCENT, outline=ACCENT)
    mid, w = size / 2, max(2, px(2.8))
    c.create_line(mid, size * 0.24, mid, size * 0.62, fill=BG, width=w,
                  arrow="last", arrowshape=(px(7), px(7), px(5)), capstyle="round")
    c.create_line(size * 0.30, size * 0.76, size * 0.70, size * 0.76, fill=BG, width=w, capstyle="round")
    return c


def window_icon(root):
    icon = tk.PhotoImage(width=32, height=32)
    icon.put(ACCENT, to=(0, 0, 32, 32))
    icon.put(BG, to=(14, 6, 18, 18))
    for i in range(6):
        icon.put(BG, to=(9 + i, 16 + i, 23 - i, 17 + i))
    icon.put(BG, to=(9, 25, 23, 27))
    root.iconphoto(True, icon)
    root._icon = icon
    ico = APP / "videofetch.ico"
    if sys.platform == "win32" and ico.exists():
        try:
            root.iconbitmap(default=str(ico))
        except tk.TclError:
            pass


def dark_title_bar(root):
    """Barra de título oscura y del mismo color que la ventana (Windows 10/11)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        dwm = ctypes.windll.dwmapi
        dark = ctypes.c_int(1)
        for attribute in (20, 19):
            if dwm.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(dark), ctypes.sizeof(dark)) == 0:
                break
        r, g, b = (int(BG[i:i + 2], 16) for i in (1, 3, 5))
        color = ctypes.c_int(r | (g << 8) | (b << 16))
        dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color), ctypes.sizeof(color))
    except Exception:
        pass


def label(parent, text="", font="body", fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=F[font], fg=fg, bg=parent["bg"], **kw)


def eyebrow(parent, number, text):
    return label(parent, f"{number} — {text.upper()}", "eyebrow", FAINT)


FORMAT_HINTS = [
    "Vídeo con audio",
    "Solo audio",
]
QUALITY_HINTS = [
    "Hasta 720p · Ocupa menos espacio",
    "Hasta 1080p · Alta definición",
    "La mejor calidad",
]
QUALITY_MP3_HINT = "Audio en MP3"
BROWSER_KEYS = ["firefox", "chrome"]
BROWSER_HINTS = [
    "Cookies de Firefox",
    "Cookies de Chrome",
]
SETTINGS = APP / "videofetch_ajustes.json"


def load_settings():
    try:
        import json
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(**values):
    try:
        import json
        data = load_settings()
        data.update(values)
        SETTINGS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


# ── Aplicación ────────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.running = False
        self.cancel = threading.Event()
        setup_fonts(root)
        root.title("VideoFetch")
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)
        window_icon(root)
        dark_title_bar(root)

        self.area = ScrollArea(root)
        self.area.pack(fill="both", expand=True)
        frame = tk.Frame(self.area.content, bg=BG)
        frame.pack(fill="both", expand=True, padx=px(36), pady=(px(28), px(30)))

        # Cabecera
        header = tk.Frame(frame, bg=BG)
        header.pack(fill="x")
        make_logo(header).pack(side="left")
        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", padx=(px(12), 0))
        label(brand, "VideoFetch", "brand").pack(anchor="w")
        label(brand, "Descargador de vídeos", "small", MUTED).pack(anchor="w")
        Chip(header, f"v{APP_VERSION}", fg=MUTED, font=F["mono"]).pack(side="right")

        # Presentación
        label(frame, "Tus vídeos, en tu equipo", "title").pack(anchor="w", pady=(px(34), px(6)))
        label(frame, "Guarda tus vídeos directamente en tu equipo, sin anuncios ni registros.",
              "lead", MUTED).pack(anchor="w", pady=(0, px(28)))

        # Tarjeta principal
        card = Panel(frame)
        card.pack(fill="both", expand=True)
        body = card.inner

        heading = tk.Frame(body, bg=SURFACE)
        heading.pack(fill="x")
        eyebrow(heading, "01", "Enlaces").pack(side="left")
        self.counter = Chip(heading, "0 vídeos", fg=MUTED)
        self.counter.pack(side="right")
        label(body, "Un enlace por línea · Los repetidos se descargan una sola vez",
              "body", MUTED).pack(anchor="w", pady=(px(2), px(14)))

        self.field = Panel(body, bg=FIELD, border=BORDER, radius=12, pad=6)
        self.field.pack(fill="both", expand=True)
        self.urls = tk.Text(self.field.inner, height=5, wrap="word", font=F["input"], undo=True,
                            bg=FIELD, fg=TEXT, insertbackground=ACCENT, insertwidth=px(2),
                            selectbackground=ACCENT_SOFT, selectforeground=TEXT, relief="flat", bd=0,
                            highlightthickness=0, padx=px(10), pady=px(8))
        icons = tk.Frame(self.field.inner, bg=FIELD)
        icons.pack(side="right", fill="y", padx=(px(4), px(6)), pady=px(6))
        self.paste_icon = IconButton(icons, "paste", self.paste_links, confirm=False)
        self.paste_icon.pack(pady=(0, px(8)))
        self.clear_icon = IconButton(icons, "clear", lambda: self.urls.delete("1.0", "end"), confirm=False)
        self.clear_icon.pack()
        self.urls.pack(fill="both", expand=True)
        SlimScrollbar(self.field.inner, self.urls)
        self.placeholder = tk.Label(self.urls, text="Pega aquí tus enlaces de YouTube, TikTok o Instagram", font=F["input"],
                                    fg=FAINT, bg=FIELD, cursor="xterm")
        self.placeholder.place(x=px(10), y=px(8))
        self.placeholder.bind("<Button-1>", lambda e: self.urls.focus_set())
        self.urls.bind("<<Modified>>", self.update_count)
        self.urls.bind("<FocusIn>", lambda e: self.field.set_border(ACCENT))
        self.urls.bind("<FocusOut>", lambda e: self.field.set_border(BORDER))
        self.urls.bind("<Control-Return>", self.shortcut)
        root.bind("<Control-Return>", self.shortcut)


        def divider():
            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=px(20))

        def option_row(number, title, hint_var):
            row = tk.Frame(body, bg=SURFACE)
            row.pack(fill="x")
            text = tk.Frame(row, bg=SURFACE)
            text.pack(side="left", fill="x", expand=True)
            eyebrow(text, number, title).pack(anchor="w")
            label(text, textvariable=hint_var, font="body", fg=MUTED).pack(anchor="w", pady=(px(4), 0))
            return row

        divider()
        self.format_hint = tk.StringVar(value=FORMAT_HINTS[0])
        row = option_row("02", "Formato", self.format_hint)
        self.media = Segmented(row, ["MP4  Vídeo", "MP3  Audio"], index=0, command=self.on_format, min_width=250)
        self.media.pack(side="right")

        divider()
        self.quality_hint = tk.StringVar(value=QUALITY_HINTS[2])
        row = option_row("03", "Calidad", self.quality_hint)
        self.quality = Segmented(row, ["720p", "1080p", "Máxima"], index=2,
                                 command=lambda i: self.quality_hint.set(QUALITY_HINTS[i]), min_width=250)
        self.quality.pack(side="right")

        divider()
        eyebrow(body, "04", "Nombre del archivo").pack(anchor="w", pady=(0, px(10)))
        # Una casilla por enlace (con 0 o 1 enlace, una sola). Vacía = nombre automático.
        self.names_holder = tk.Frame(body, bg=SURFACE)
        self.names_holder.pack(fill="x")
        self.name_vars = {}
        self.name_fields = []
        self.shown_links = None
        self.build_names([])

        divider()
        row = tk.Frame(body, bg=SURFACE)
        row.pack(fill="x")
        text = tk.Frame(row, bg=SURFACE)
        text.pack(side="left", fill="x", expand=True)
        eyebrow(text, "05", "Destino").pack(anchor="w")
        label(text, "VIDEOFETCH \\ DOWNLOADS", "mono", TEXT).pack(anchor="w", pady=(px(5), 0))
        Button(row, "Abrir carpeta", self.open_folder, height=36, padx=16).pack(side="right")

        # Cookies: línea pequeña al final de la tarjeta
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(px(20), px(12)))
        saved = load_settings().get("browser")
        browser_index = BROWSER_KEYS.index(saved) if saved in BROWSER_KEYS else 0
        self.browser_hint = tk.StringVar(value=BROWSER_HINTS[browser_index])
        row = tk.Frame(body, bg=SURFACE)
        row.pack(fill="x")
        label(row, textvariable=self.browser_hint, font="tiny", fg=FAINT).pack(side="left")
        self.browser = Segmented(row, ["Firefox", "Chrome"], index=browser_index,
                                 command=self.on_browser, compact=True)
        self.browser.pack(side="right")

        # Estado y progreso
        status_row = tk.Frame(frame, bg=BG)
        status_row.pack(fill="x", pady=(px(26), px(10)))
        self.dot = tk.Canvas(status_row, width=px(8), height=px(8), bg=BG, highlightthickness=0, bd=0)
        self.dot.create_oval(0, 0, px(8), px(8), fill=FAINT, outline="", tags="dot")
        self.dot.pack(side="left", padx=(0, px(10)))
        self.status = tk.StringVar(value="Todo listo · Añade tus enlaces para comenzar")
        label(status_row, textvariable=self.status, font="body", fg=TEXT, anchor="w").pack(
            side="left", fill="x", expand=True)
        self.percent = tk.StringVar(value="")
        label(status_row, textvariable=self.percent, font="mono", fg=MUTED).pack(side="right")
        self.progress = Progress(frame)
        self.progress.pack(fill="x")

        # Acciones
        actions = tk.Frame(frame, bg=BG)
        actions.pack(fill="x", pady=(px(22), 0))
        self.details_button = Button(actions, "Ver actividad", self.toggle_details, kind="ghost", height=40, padx=14)
        self.details_button.pack(side="left")
        self.start_button = Button(actions, "Descargar", self.start, kind="primary", height=44, padx=26)
        self.start_button.pack(side="right")
        self.stop_button = Button(actions, "Detener", self.stop, height=44, padx=20)
        self.stop_button.configure(state="disabled")
        self.stop_button.pack(side="right", padx=px(10))

        self.details = Panel(frame, bg=FIELD, radius=12, pad=12)
        self.log = tk.Text(self.details.inner, height=7, wrap="word", state="disabled", font=F["mono"],
                           bg=FIELD, fg=MUTED, relief="flat", bd=0, highlightthickness=0,
                           selectbackground=ACCENT_SOFT, padx=px(4), pady=px(2))
        self.log.pack(fill="both", expand=True)
        SlimScrollbar(self.details.inner, self.log)
        self.copy_icon = IconButton(self.details.inner, "copy", self.copy_log)
        self.copy_icon.place(relx=1.0, x=-px(18), y=px(2), anchor="ne")

        self.card, self.frame = card, frame
        self.fit_window()
        self.root.after(100, self.poll)

    def required_height(self):
        """Altura real que necesita la ventana (las tarjetas redondeadas se miden aparte)."""
        for _ in range(2):
            self.root.update_idletasks()
            self.field._fit()
            for field in self.name_fields:
                field.panel._fit()
            self.card._fit()
            if self.details.winfo_manager():
                self.details._fit()
        self.root.update_idletasks()
        return self.area.needed_height()

    def fit_window(self):
        """Abre la ventana con el tamaño justo para que no se corte nada.
        En pantallas bajas, encoge el cuadro de enlaces y la deja centrada."""
        usable = self.root.winfo_screenheight() - px(90)
        for lines in (5, 4, 3):
            self.urls.configure(height=lines)
            needed = self.required_height()
            if needed <= usable:
                break
        width = max(px(880), self.area.content.winfo_reqwidth())
        height = min(needed, usable)
        x = max(0, (self.root.winfo_screenwidth() - width) // 2)
        y = max(0, (usable - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(px(780), px(420))

    # ── Utilidades de interfaz ──
    def on_browser(self, index):
        self.browser_hint.set(BROWSER_HINTS[index])
        save_settings(browser=BROWSER_KEYS[index])

    def audio(self):
        return self.media.current() == 1

    def on_format(self, index):
        self.format_hint.set(FORMAT_HINTS[index])
        if self.audio():
            self.quality.configure(state="disabled")
            self.quality_hint.set(QUALITY_MP3_HINT)
            self.start_button.configure(text="Descargar")
        else:
            self.quality.configure(state="normal")
            self.quality_hint.set(QUALITY_HINTS[self.quality.current()])
            self.start_button.configure(text="Descargar")

    def set_dot(self, color):
        self.dot.itemconfigure("dot", fill=color)

    def shortcut(self, event=None):
        if not self.running:
            self.start()
        return "break"

    def paste_links(self):
        if self.running:
            return
        try:
            text = self.root.clipboard_get().strip()
        except tk.TclError:
            return
        if text:
            existing = self.urls.get("1.0", "end-1c")
            self.urls.insert("end", ("\n" if existing and not existing.endswith("\n") else "") + text + "\n")
            self.urls.see("end")

    def update_count(self, event=None):
        if not self.urls.edit_modified():
            return
        content = self.urls.get("1.0", "end")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        count = len(set(lines))
        repeated = len(lines) - count
        text = f"{count} vídeo{'s' if count != 1 else ''}"
        if repeated:
            text += f" · {repeated} repetido{'s' if repeated != 1 else ''}"
        self.counter.set_text(text, fg=TEXT if count else MUTED)
        if content.strip():
            self.placeholder.place_forget()
        else:
            self.placeholder.place(x=px(10), y=px(8))
        self.urls.edit_modified(False)
        self.build_names(list(dict.fromkeys(lines)))

    def name_var(self, key):
        if key not in self.name_vars:
            self.name_vars[key] = tk.StringVar()
        return self.name_vars[key]

    def build_names(self, links):
        """Rehace la lista de casillas de nombre cuando cambian los enlaces."""
        if tuple(links) == self.shown_links:
            return
        self.shown_links = tuple(links)
        # Lo escrito antes de pegar el primer enlace pasa a ese enlace.
        if links and self.name_vars.get("") and self.name_vars[""].get() and not self.name_var(links[0]).get():
            self.name_var(links[0]).set(self.name_vars[""].get())
            self.name_vars[""].set("")
        for child in self.names_holder.winfo_children():
            child.destroy()
        self.name_fields = []
        if len(links) <= 1:
            field = NameField(self.names_holder, self.name_var(links[0] if links else ""), self.shortcut)
            field.pack(fill="x")
            self.name_fields.append(field)
        else:
            visible = 4
            canvas = tk.Canvas(self.names_holder, bg=SURFACE, highlightthickness=0, bd=0, height=1)
            inner = tk.Frame(canvas, bg=SURFACE)
            window = canvas.create_window(0, 0, window=inner, anchor="nw")
            canvas.pack(side="left", fill="x", expand=True, anchor="n")
            for index, link in enumerate(links, 1):
                row = tk.Frame(inner, bg=SURFACE)
                row.pack(fill="x", pady=(0, px(6)))
                tk.Label(row, text=f"{index:>2} · {short_link(link)}", font=F["mono"], fg=FAINT, bg=SURFACE,
                         width=36, anchor="w").pack(side="left", padx=(0, px(10)))
                field = NameField(row, self.name_var(link), self.shortcut)
                field.pack(side="left", fill="x", expand=True)
                self.name_fields.append(field)
            for widget in (canvas, inner):
                widget.wheel_target = canvas
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=(0, 0, e.width, e.height)))
            canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
            self.root.update_idletasks()
            row_height = inner.winfo_reqheight() / len(links)
            canvas.configure(height=int(row_height * min(len(links), visible)), yscrollincrement=int(row_height))
            if len(links) > visible:
                SlimScrollbar(self.names_holder, canvas)
            for widget in inner.winfo_children():
                widget.wheel_target = canvas
        if self.running:
            for field in self.name_fields:
                field.set_state("disabled")
        self.relayout()

    def relayout(self):
        """Recalcula alturas cuando cambia el contenido (más casillas, actividad...)."""
        if not hasattr(self, "card"):
            return
        self.required_height()
        self.area._resize()

    def toggle_details(self):
        if self.details.winfo_manager():
            self.details.pack_forget()
            self.details_button.configure(text="Ver actividad")
        else:
            self.details.pack(fill="x", pady=(px(14), 0))
            self.details_button.configure(text="Ocultar actividad")
            needed = self.required_height()
            self.area._resize()
            usable = self.root.winfo_screenheight() - px(90)
            self.root.geometry(f"{self.root.winfo_width()}x{min(usable, max(self.root.winfo_height(), needed))}")

    def open_folder(self):
        folder = DOWNLOADS
        folder.mkdir(exist_ok=True)
        os.startfile(str(folder))

    def set_inputs(self, enabled):
        state = "normal" if enabled else "disabled"
        self.urls.configure(state=state, fg=TEXT if enabled else MUTED)
        self.paste_icon.set_state(state)
        self.clear_icon.set_state(state)
        self.media.configure(state=state)
        self.browser.configure(state=state)
        for field in self.name_fields:
            field.set_state(state)
        self.quality.configure(state="normal" if enabled and not self.audio() else "disabled")
        self.start_button.configure(state=state)
        self.stop_button.configure(state="disabled" if enabled else "normal")

    def copy_log(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log.get("1.0", "end-1c"))

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── Descarga ──
    def start(self):
        urls = list(dict.fromkeys(line.strip() for line in self.urls.get("1.0", "end").splitlines() if line.strip()))
        if not urls or any(not url.startswith(("https://", "http://")) for url in urls):
            messagebox.showinfo("Revisa los enlaces", "Pega un enlace completo https://… por línea.")
            return
        if not shutil.which("ffmpeg"):
            messagebox.showerror("Falta FFmpeg", "No se encuentra FFmpeg, necesario para unir y convertir el vídeo y el audio.")
            return
        self.running = True
        self.note = None
        self.cancel.clear()
        self.set_inputs(False)
        self.set_dot(ACCENT)
        self.progress.set(0, ACCENT)
        self.percent.set("0 %")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        quality = ("720", "1080", "original")[self.quality.current()]
        browser = BROWSER_KEYS[self.browser.current()]
        names = {url: self.name_var(url).get().strip() for url in urls}
        if len(urls) == 1 and not names[urls[0]]:
            names[urls[0]] = self.name_var("").get().strip()
        threading.Thread(target=self.download, args=(urls, quality, self.audio(), browser, names),
                         daemon=True).start()

    def stop(self):
        self.cancel.set()
        self.status.set("Deteniendo…")
        self.set_dot(WARNING)
        self.stop_button.configure(state="disabled")

    def download(self, urls, quality, audio, browser=None, names=None):
        app = self

        class Logger:
            def debug(self, message):
                if not message.startswith("[debug]"):
                    app.events.put(("log", message))

            def warning(self, message):
                app.events.put(("log", "Aviso: " + message))

            def error(self, message):
                app.events.put(("log", message))

        def hook(data):
            if app.cancel.is_set():
                raise yt_dlp.utils.DownloadError("Descarga detenida por el usuario")
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            if data["status"] == "downloading" and total:
                app.events.put(("progress", min(100, data.get("downloaded_bytes", 0) / total * 100)))
            elif data["status"] == "finished":
                app.events.put(("status", "Convirtiendo a MP3…" if audio else "Uniendo vídeo y audio…"))

        def notify(kind, text=""):
            if kind == "status":
                app.events.put(("status", text))
            elif kind == "progress":
                app.events.put(("progress", text))
            elif kind == "note":
                app.events.put(("note", text))
                app.events.put(("log", "Calidad: " + text))
            elif kind == "incognito":
                app.events.put(("status", text))
                app.events.put(("log", "— " + text))
                app.events.put(("progress", 0))
            else:
                app.events.put(("log", text))

        extra = dict(logger=Logger(), progress_hooks=[hook], noprogress=True, quiet=True)
        failures = 0
        completed = 0
        try:
            output = DOWNLOADS
            output.mkdir(exist_ok=True)
            for index, url in enumerate(urls, 1):
                if self.cancel.is_set():
                    break
                self.events.put(("status", f"Descargando {index} de {len(urls)}"))
                self.events.put(("progress", 0))
                ok = core.download(url, output, quality, audio, extra=extra, notify=notify, browser=browser,
                                   custom_name=(names or {}).get(url) or None,
                                   cancelled=self.cancel.is_set)
                if self.cancel.is_set():
                    break
                if ok:
                    completed += 1
                else:
                    failures += 1
        except Exception as exc:
            failures += 1
            self.events.put(("log", str(exc)))
        finally:
            self.events.put(("done", (completed, failures, self.cancel.is_set())))

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.write_log(value)
                elif kind == "progress":
                    self.progress.set(value)
                    self.percent.set(f"{value:.0f} %")
                elif kind == "note":
                    self.note = value
                elif kind == "done":
                    self.finish(*value)
                elif not self.cancel.is_set():
                    self.status.set(value)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def finish(self, completed, failures, stopped):
        self.running = False
        self.set_inputs(True)
        done = f"{completed} descargado{'s' if completed != 1 else ''}"
        if stopped:
            self.status.set(f"Detenido · {done}" + (f" · {failures} con error" if failures else ""))
            color = WARNING
        elif failures:
            self.status.set(f"Terminado · {done} · {failures} con error. Mira la actividad para ver el motivo.")
            color = DANGER if not completed else WARNING
        else:
            where = "Ya está" if completed == 1 else "Ya están"
            if self.note:
                self.status.set(f"Listo · {done} · {self.note}")
            else:
                self.status.set(f"Listo · {done}. {where} en la carpeta DOWNLOADS.")
            for variable in self.name_vars.values():
                variable.set("")
            color = SUCCESS
            self.progress.set(100)
            self.percent.set("100 %")
        self.set_dot(color)
        self.progress.set(self.progress.value, color)

    def close(self):
        if self.running:
            messagebox.showinfo("Descarga en marcha", "Pulsa Detener y espera a que termine antes de cerrar.")
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
