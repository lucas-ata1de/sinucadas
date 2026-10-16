#!/usr/bin/env python3
"""
Utilitários de ambiente para scripts de Computação Gráfica.
Contém funções auxiliares de plataforma (cursor, janela, ícone) e utilitários
otimizados para ModernGL/GLFW (inicialização, compilação de shaders, temporização,
recarga a quente e liberação determinística de recursos).
"""

import configparser
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Any

import glfw
import moderngl
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


def configure_cursor() -> None:
    """Configura as variáveis de ambiente XCURSOR para evitar distorções do cursor no Wayland/X11."""
    base_paths = [
        str(Path.home() / ".local" / "share" / "icons"),
        str(Path.home() / ".icons"),
        "/usr/local/share/icons",
        "/usr/share/icons",
    ]
    if not os.environ.get("XCURSOR_PATH"):
        valid_paths = [p for p in base_paths if Path(p).is_dir()]
        if valid_paths:
            os.environ["XCURSOR_PATH"] = ":".join(valid_paths)

    if "XCURSOR_THEME" in os.environ and "XCURSOR_SIZE" in os.environ:
        return

    detected_theme = None
    detected_size = None

    default_theme_file = Path.home() / ".icons" / "default" / "index.theme"
    if default_theme_file.is_file():
        with suppress(Exception):
            parser = configparser.ConfigParser()
            parser.read(default_theme_file)
            if parser.has_option("Icon Theme", "Inherits"):
                val = parser.get("Icon Theme", "Inherits").strip()
                if val:
                    detected_theme = val

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

    for cfg_path, section, theme_key, size_key in config_candidates:
        if not cfg_path.is_file():
            continue
        with suppress(Exception):
            parser = configparser.ConfigParser()
            parser.read(cfg_path)
            if not detected_theme and parser.has_option(section, theme_key):
                val = parser.get(section, theme_key).strip()
                if val:
                    detected_theme = val
            if not detected_size and parser.has_option(section, size_key):
                val = str(parser.getint(section, size_key))
                if val:
                    detected_size = val
            if detected_theme and detected_size:
                break

    if (not detected_theme or not detected_size) and shutil.which("gsettings"):
        with suppress(Exception):
            if not detected_theme:
                res = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "cursor-theme"],
                    capture_output=True,
                    text=True,
                    timeout=0.2,
                )
                if res.returncode == 0:
                    val = res.stdout.strip().strip("'\"")
                    if val:
                        detected_theme = val
            if not detected_size:
                res = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "cursor-size"],
                    capture_output=True,
                    text=True,
                    timeout=0.2,
                )
                if res.returncode == 0:
                    val = res.stdout.strip().strip("'\"")
                    if val and val.isdigit():
                        detected_size = val

    if not detected_theme:
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
        if "KDE" in desktop:
            detected_theme = "breeze_cursors"
        elif any(d in desktop for d in ("GNOME", "UBUNTU")):
            detected_theme = "Adwaita"
        else:
            detected_theme = "default"

    if not detected_size:
        detected_size = "24"

    os.environ.setdefault("XCURSOR_THEME", detected_theme)
    os.environ.setdefault("XCURSOR_SIZE", detected_size)


def configure_window_hint(app_id: str = "moderngl") -> None:
    """Configura identificadores de plataforma (Wayland app_id e X11 WM_CLASS) antes de glfw.create_window."""
    if hasattr(glfw, "WAYLAND_APP_ID"):
        glfw.window_hint_string(glfw.WAYLAND_APP_ID, app_id)
    if hasattr(glfw, "X11_CLASS_NAME"):
        glfw.window_hint_string(glfw.X11_CLASS_NAME, app_id)


def glfw_error_callback(code: int, msg: str) -> None:
    """Callback padrão de erros do GLFW direcionado ao stderr."""
    print(f"GLFW [{code}]: {msg}", file=sys.stderr)


# -----------------------------------------------------------------------------
# Subsistema de Hot-Reload de Shaders
# -----------------------------------------------------------------------------
_HOT_RELOAD_ENABLED: bool = True
_HOT_RELOAD_KEY: int = getattr(glfw, "KEY_F4", 293)
_HOT_RELOAD_LISTENERS: list[Callable[[], Any]] = []


def configure_hot_reload(enabled: bool = True, key: int | None = None) -> None:
    """Ativa ou desativa o hot-reload de shaders e opcionalmente configura a tecla de disparo (padrão F4)."""
    global _HOT_RELOAD_ENABLED, _HOT_RELOAD_KEY
    _HOT_RELOAD_ENABLED = enabled
    if key is not None:
        _HOT_RELOAD_KEY = key


def is_hot_reload_enabled() -> bool:
    """Retorna se o hot-reload de shaders está atualmente habilitado."""
    return _HOT_RELOAD_ENABLED


def get_hot_reload_key() -> int:
    """Retorna o código GLFW da tecla atualmente associada ao disparo do hot-reload."""
    return _HOT_RELOAD_KEY


def register_hot_reload(callback: Callable[[], Any]) -> None:
    """Registra uma função de callback para recompilar shaders e reconstruir o pipeline no hot-reload."""
    if callback not in _HOT_RELOAD_LISTENERS:
        _HOT_RELOAD_LISTENERS.append(callback)


def unregister_hot_reload(callback: Callable[[], Any]) -> None:
    """Remove uma função de callback de hot-reload previamente registrada."""
    if callback in _HOT_RELOAD_LISTENERS:
        _HOT_RELOAD_LISTENERS.remove(callback)


def clear_hot_reload_listeners() -> None:
    """Limpa todas as funções de callback de hot-reload registradas."""
    _HOT_RELOAD_LISTENERS.clear()


def trigger_hot_reload() -> bool:
    """Dispara manualmente todos os callbacks de hot-reload registrados com tratamento seguro de erros."""
    if not _HOT_RELOAD_ENABLED:
        return False

    print("\n[HOT-RELOAD] 🔄 Disparando recarga de shaders e pipeline...", flush=True)
    if not _HOT_RELOAD_LISTENERS:
        print("[HOT-RELOAD] ℹ️  Hot-reload acionado, mas nenhum callback foi registrado.", flush=True)
        return True

    success = True
    for callback in _HOT_RELOAD_LISTENERS:
        try:
            callback()
        except Exception as exc:
            print(f"[HOT-RELOAD] ❌ Erro ao recarregar pipeline: {exc}", file=sys.stderr, flush=True)
            success = False

    if success:
        print("[HOT-RELOAD] ✅ Pipeline e shaders recarregados com sucesso!\n", flush=True)
    return success


def check_hot_reload_key(key: int, action: int) -> bool:
    """Verifica se o evento de teclado corresponde à tecla de hot-reload configurada (padrão F4)."""
    if _HOT_RELOAD_ENABLED and action == glfw.PRESS and key == _HOT_RELOAD_KEY:
        trigger_hot_reload()
        return True
    return False


_ORIGINAL_GLFW_SET_KEY_CALLBACK = glfw.set_key_callback


def set_key_callback(
    window: Any,
    user_callback: Callable[[Any, int, int, int, int], None] | None = None,
) -> None:
    """Define um callback de teclado GLFW na janela interceptando automaticamente a tecla de hot-reload."""
    def _key_handler(win: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if check_hot_reload_key(key, action):
            return
        if user_callback is not None:
            user_callback(win, key, scancode, action, mods)

    _ORIGINAL_GLFW_SET_KEY_CALLBACK(window, _key_handler)


def _glfw_set_key_callback_hook(
    window: Any,
    cbfun: Callable[[Any, int, int, int, int], None] | None,
) -> Any:
    return set_key_callback(window, cbfun)


glfw.set_key_callback = _glfw_set_key_callback_hook


def window_setup(
    size: tuple[int, int] = (800, 600),
    title: str = "ModernGL",
    resizable: bool = True,
    vsync: bool = True,
    gl_version: tuple[int, int] = (4, 0),
    samples_msaa: int = 4,
    app_id: str = "moderngl",
    icon_path: Path | str | None = DEFAULT_ICON,
    enable_hot_reload: bool = True,
    hot_reload_key: int | None = None,
    depth_test: bool = False,
    cull_face: bool = False,
    blend: bool = False,
) -> tuple[Any, moderngl.Context]:
    """Inicializa o GLFW, define hints de plataforma, cria janela e contexto ModernGL e aplica o ícone."""
    configure_hot_reload(enabled=enable_hot_reload, key=hot_reload_key)
    configure_cursor()
    glfw.set_error_callback(glfw_error_callback)

    if not glfw.init():
        sys.exit("FALHA: Não foi possível inicializar o GLFW")

    major, minor = gl_version
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.SAMPLES, samples_msaa)
    glfw.window_hint(glfw.RESIZABLE, resizable)
    glfw.window_hint(glfw.DEPTH_BITS, 24)

    configure_window_hint(app_id)

    window = glfw.create_window(*size, title, None, None)
    if not window:
        glfw.terminate()
        sys.exit("FALHA: Não foi possível criar a janela GLFW")

    glfw.make_context_current(window)
    glfw.swap_interval(1 if vsync else 0)
    apply_icon(window, icon_path)
    set_key_callback(window, None)

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, *glfw.get_framebuffer_size(window))

    if depth_test:
        ctx.enable(moderngl.DEPTH_TEST)
    if cull_face:
        ctx.enable(moderngl.CULL_FACE)
    if blend:
        ctx.enable(moderngl.BLEND)

    return window, ctx


def read_shader(path: Path | str, name: str | None = None) -> str:
    """Lê um arquivo de shader em disco utilizando codificação UTF-8."""
    shader_path = Path(path)
    if name is not None:
        shader_path = shader_path / name
    return shader_path.read_text(encoding="utf-8")


def create_program(
    ctx: moderngl.Context,
    vertex_shader: str | Path,
    fragment_shader: str | Path | None = None,
    geometry_shader: str | Path | None = None,
    tess_control_shader: str | Path | None = None,
    tess_evaluation_shader: str | Path | None = None,
) -> moderngl.Program:
    """Compila e vincula um programa ModernGL a partir de arquivos (Path) ou strings de código GLSL."""

    def _get_code(source: str | Path | None) -> str | None:
        if source is None:
            return None
        if isinstance(source, Path) or (
            isinstance(source, str) and "\n" not in source and Path(source).is_file()
        ):
            return Path(source).read_text(encoding="utf-8")
        return str(source)

    vs = _get_code(vertex_shader)
    fs = _get_code(fragment_shader)
    gs = _get_code(geometry_shader)
    tcs = _get_code(tess_control_shader)
    tes = _get_code(tess_evaluation_shader)

    try:
        kwargs: dict[str, Any] = {"vertex_shader": vs}
        if fs is not None:
            kwargs["fragment_shader"] = fs
        if gs is not None:
            kwargs["geometry_shader"] = gs
        if tcs is not None:
            kwargs["tess_control_shader"] = tcs
        if tes is not None:
            kwargs["tess_evaluation_shader"] = tes
        return ctx.program(**kwargs)
    except moderngl.Error as err:
        print(f"\n[ERRO DE COMPILAÇÃO DE SHADER]\n{err}\n", file=sys.stderr)
        raise


def create_compute_shader(
    ctx: moderngl.Context,
    compute_shader: str | Path,
) -> moderngl.ComputeShader:
    """Compila um Compute Shader no ModernGL a partir de caminho de arquivo ou string GLSL."""
    if isinstance(compute_shader, Path) or (
        isinstance(compute_shader, str) and "\n" not in compute_shader and Path(compute_shader).is_file()
    ):
        code = Path(compute_shader).read_text(encoding="utf-8")
    else:
        code = str(compute_shader)
    return ctx.compute_shader(code)


def load_texture(
    ctx: moderngl.Context,
    path: Path | str,
    flip_y: bool = True,
    build_mipmaps: bool = True,
) -> moderngl.Texture:
    """Carrega uma imagem em disco como textura 2D no ModernGL com inversão vertical de UV e mipmaps."""
    img = Image.open(path)
    if flip_y:
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    img = img.convert("RGBA")
    tex = ctx.texture(img.size, 4, img.tobytes())
    if build_mipmaps:
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    else:
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
    return tex


def capture_mouse(window: Any, capture: bool = True) -> None:
    """Captura ou libera o cursor do mouse para navegação em primeira pessoa (FPS) ou orbital."""
    mode = glfw.CURSOR_DISABLED if capture else glfw.CURSOR_NORMAL
    glfw.set_input_mode(window, glfw.CURSOR, mode)
    if hasattr(glfw, "raw_mouse_motion_supported") and glfw.raw_mouse_motion_supported():
        glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, glfw.TRUE if capture else glfw.FALSE)


def get_aspect_ratio(window: Any) -> float:
    """Calcula a razão de aspecto do framebuffer (largura / altura) para matrizes de projeção perspectiva."""
    width, height = glfw.get_framebuffer_size(window)
    return width / height if height > 0 else 1.0


def get_projection_scale(window: Any) -> tuple[float, float]:
    """Calcula os fatores de projeção (sx, sy) para ajustar a cena sem distorção e sem transbordar."""
    width, height = glfw.get_framebuffer_size(window)
    if width <= 0 or height <= 0:
        return 1.0, 1.0
    aspect = width / height
    sy = min(1.75, 0.98 * aspect)
    sx = sy / aspect
    return sx, sy


def adjust_viewport(ctx: moderngl.Context, size: tuple[int, int]) -> bool:
    """Atualiza o viewport do ModernGL apenas se largura e altura forem positivas (evita crash ao minimizar)."""
    width, height = size
    if width > 0 and height > 0:
        ctx.viewport = (0, 0, width, height)
        return True
    return False


def update_time(before: float, dt_max: float | None = None) -> tuple[float, float]:
    """Calcula o tempo atual e delta time, com clamp opcional em dt_max para estabilidade da física."""
    now = glfw.get_time()
    dt = now - before
    if dt_max is not None and dt_max > 0 and dt > dt_max:
        dt = dt_max
    return now, dt


def release_resource(*resources: Any) -> None:
    """Libera recursos ModernGL com segurança, desempacotando recursivamente listas, tuplas, sets e dicts."""
    for res in resources:
        if res is None:
            continue
        if isinstance(res, (list, tuple, set)):
            release_resource(*res)
        elif isinstance(res, dict):
            release_resource(*res.values())
        elif hasattr(res, "release"):
            with suppress(Exception):
                res.release()


if __name__ == "__main__":
    configure_cursor()
    print(
        f"environment.py: XCURSOR_THEME={os.environ.get('XCURSOR_THEME')}, "
        f"XCURSOR_SIZE={os.environ.get('XCURSOR_SIZE')}"
    )
