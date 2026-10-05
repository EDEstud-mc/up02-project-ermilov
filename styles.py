import tkinter as tk

COLOR_MAIN_BG = "#FFFFFF"
COLOR_SECONDARY_BG = "#D2F6E7"
COLOR_ACCENT = "#70B2AF"
COLOR_HIGHLIGHT = "#ff8080"

FONT_FAMILY = "Calibri"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_HEADER = 14
FONT_SIZE_TITLE = 18

def font(size=FONT_SIZE_NORMAL, bold=False):
    """Возвращает настройки шрифта."""
    return (FONT_FAMILY, size, "bold" if bold else "normal")

def make_button(parent, text, command):
    """Создаёт кнопку в стиле КИМ."""
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLOR_ACCENT,
        fg="#FFFFFF",
        font=font(),
        relief="flat",
        padx=15,
        pady=5,
        activebackground=COLOR_ACCENT,
        cursor="hand2"
    )
