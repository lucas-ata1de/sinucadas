#!/usr/bin/env python3
"""
Utilitários de ambiente e plataforma para o Sinucadas.
Gerencia configuração de cursor do mouse (XCURSOR) e ícone da janela para Wayland e X11.
"""

import configparser
import os
from contextlib import suppress
from pathlib import Path
from typing import Any

import glfw
from PIL import Image

DEFAULT_ICON = Path(__file__).resolve().parent / "moderngl.png"


def apply_icon(window: Any, path: Path | str | None = None) -> None:
    """Aplica o ícone da janela no GLFW caso não esteja rodando sob Wayland nativo."""
    is_wayland = (
        glfw.get_platform() == getattr(glfw, "PLATFORM_WAYLAND", -1)
        if hasattr(glfw, "get_platform")
        else bool(os.environ.get("WAYLAND_DISPLAY"))
    )
    if is_wayland:
        return

    icon_path = Path(path) if path else DEFAULT_ICON
    if icon_path.exists():
        with suppress(Exception):
            icon_img = Image.open(icon_path).convert("RGBA")
            glfw.set_window_icon(window, 1, [icon_img])  # type: ignore[arg-type]


def _setup_xcursor_path(base_paths: list[str]) -> None:
    """Configura XCURSOR_PATH caso ainda não definido."""
    if not os.environ.get("XCURSOR_PATH"):
        valid_paths = [p for p in base_paths if Path(p).is_dir()]
        if valid_paths:
            os.environ["XCURSOR_PATH"] = ":".join(valid_paths)


def _detect_theme_from_index() -> str | None:
    """Tenta detectar o tema de cursor padrão a partir do arquivo ~/.icons/default/index.theme."""
    default_theme_file = Path.home() / ".icons" / "default" / "index.theme"
    if default_theme_file.is_file():
        with suppress(Exception):
            parser = configparser.ConfigParser()
            parser.read(default_theme_file)
            if parser.has_option("Icon Theme", "Inherits"):
                val = parser.get("Icon Theme", "Inherits").strip()
                if val:
                    return val
    return None


def _detect_desktop_cursor_config() -> tuple[str | None, str | None]:
    """Varre arquivos de configuração do KDE e GTK para descobrir tema e tamanho do cursor."""
    config_candidates = (
        (Path.home() / ".config" / "kcminputrc", "Mouse", "cursorTheme", "cursorSize"),
        (
            Path.home() / ".config" / "kdedefaults" / "kcminputrc",
            "Mouse",
            "cursorTheme",
            "cursorSize",
        ),
        (
            Path.home() / ".config" / "gtk-4.0" / "settings.ini",
            "Settings",
            "gtk-cursor-theme-name",
            "gtk-cursor-theme-size",
        ),
        (
            Path.home() / ".config" / "gtk-3.0" / "settings.ini",
            "Settings",
            "gtk-cursor-theme-name",
            "gtk-cursor-theme-size",
        ),
    )
    detected_theme = None
    detected_size = None

    for cfg_path, section, theme_key, size_key in config_candidates:
        if not cfg_path.is_file():
            continue
        with suppress(Exception):
            parser = configparser.ConfigParser()
            parser.read(cfg_path)
            if not detected_theme and parser.has_option(section, theme_key):
                val = parser.get(section, theme_key).strip().strip("\"'")
                if val:
                    detected_theme = val
            if not detected_size and parser.has_option(section, size_key):
                val = parser.get(section, size_key).strip().strip("\"'")
                if val.isdigit() and int(val) > 0:
                    detected_size = val
        if detected_theme and detected_size:
            break

    return detected_theme, detected_size


def _detect_fallback_cursor_theme(base_paths: list[str]) -> str | None:
    """Busca um tema de cursor padrão existente nos diretórios de ícones do sistema."""
    for theme_name in ("breeze_cursors", "Adwaita", "default"):
        if any((Path(p) / theme_name).is_dir() for p in base_paths):
            return theme_name
    return None


def configure_cursor() -> None:
    """Configura as variáveis de ambiente XCURSOR para evitar distorções do cursor no Wayland/X11."""
    base_paths = [
        str(Path.home() / ".local" / "share" / "icons"),
        str(Path.home() / ".icons"),
        "/usr/local/share/icons",
        "/usr/share/icons",
    ]
    _setup_xcursor_path(base_paths)

    if "XCURSOR_THEME" in os.environ and "XCURSOR_SIZE" in os.environ:
        return

    detected_theme = _detect_theme_from_index()
    cfg_theme, cfg_size = _detect_desktop_cursor_config()

    detected_theme = detected_theme or cfg_theme or _detect_fallback_cursor_theme(base_paths)
    detected_size = cfg_size or "24"

    if detected_theme and "XCURSOR_THEME" not in os.environ:
        os.environ["XCURSOR_THEME"] = detected_theme
    if detected_size and "XCURSOR_SIZE" not in os.environ:
        os.environ["XCURSOR_SIZE"] = detected_size


def configure_window_hint(app_id: str = "moderngl") -> None:
    """Configura identificadores de plataforma (Wayland app_id e X11 WM_CLASS) antes de glfw.create_window."""
    if hasattr(glfw, "WAYLAND_APP_ID"):
        glfw.window_hint_string(glfw.WAYLAND_APP_ID, app_id)
    if hasattr(glfw, "X11_CLASS_NAME"):
        glfw.window_hint_string(glfw.X11_CLASS_NAME, app_id)


if __name__ == "__main__":
    configure_cursor()
    print("environment.py: mouse cursor and icon environment utilities validated successfully.")
