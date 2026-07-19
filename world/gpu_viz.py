"""GPU preferences for PyVista / VTK live visualisation (AMD-safe).

Default is **safe OpenGL**: no MSAA / SSAA / depth-peeling shaders that often
fail on AMD with ``Error! Could not set shader program``.

Optional quality (if stable on your driver):
  set EQMOD_GL_QUALITY=1
"""
from __future__ import annotations

import os
import sys
from typing import Optional

_CONFIGURED = False
_LAST_RENDERER: Optional[str] = None


def request_high_performance_gpu() -> None:
    """Hint Windows / drivers to prefer the discrete GPU for this process."""
    os.environ.setdefault("AMD_POWERXPRESS_REQUEST_HIGH_PERFORMANCE", "1")
    # Avoid some broken threaded GL paths on multi-adapter laptops
    os.environ.setdefault("__GL_THREADED_OPTIMIZATIONS", "0")

    if sys.platform != "win32":
        return
    try:
        import winreg

        py = os.path.abspath(sys.executable)
        key_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, py, 0, winreg.REG_SZ, "GpuPreference=2;")
            if py.lower().endswith("python.exe"):
                pyw = py[:-10] + "pythonw.exe"
                if os.path.isfile(pyw):
                    winreg.SetValueEx(key, pyw, 0, winreg.REG_SZ, "GpuPreference=2;")
    except Exception as exc:
        print(f"[gpu_viz] registry GpuPreference skip: {exc}")


def _want_quality() -> bool:
    return os.environ.get("EQMOD_GL_QUALITY", "").strip() in ("1", "true", "yes")


def configure_pyvista_gpu(multi_samples=0, verbose=True):
    """Global PyVista theme — **safe defaults** for AMD OpenGL."""
    global _CONFIGURED
    request_high_performance_gpu()
    try:
        import pyvista as pv

        if _want_quality():
            pv.global_theme.multi_samples = max(4, multi_samples or 4)
            pv.global_theme.anti_aliasing = "msaa"
        else:
            # No MSAA shader paths (common "Could not set shader program" trigger)
            pv.global_theme.multi_samples = 0
            try:
                pv.global_theme.anti_aliasing = None
            except Exception:
                pv.global_theme.anti_aliasing = "msaa"
                pv.global_theme.multi_samples = 0
        try:
            pv.global_theme.allow_empty_mesh = True
        except Exception:
            pass
    except Exception as exc:
        print(f"[gpu_viz] pyvista theme: {exc}")
    _CONFIGURED = True
    if verbose:
        mode = "QUALITY" if _want_quality() else "SAFE (no MSAA/depth-peel)"
        print(f"[gpu_viz] OpenGL mode={mode}  exe={sys.executable}")


def apply_plotter_gpu(pl) -> str:
    """Tune plotter. Safe mode: do **not** enable MSAA/SSAA/depth peeling."""
    global _LAST_RENDERER
    configure_pyvista_gpu(0, False)
    info = "unknown"
    try:
        if _want_quality():
            try:
                pl.enable_anti_aliasing("msaa", multi_samples=4)
            except Exception:
                pass
            if os.environ.get("EQMOD_DEPTH_PEEL", "").strip() == "1":
                try:
                    pl.enable_depth_peeling(number_of_peels=4, occlusion_ratio=0.0)
                except Exception:
                    pass
        else:
            # Explicitly disable multi-sampling on the render window
            try:
                pl.disable_anti_aliasing()
            except Exception:
                pass
            rw = getattr(pl, "ren_win", None) or getattr(pl, "render_window", None)
            if rw is not None:
                try:
                    rw.SetMultiSamples(0)
                except Exception:
                    pass

        rw = getattr(pl, "ren_win", None) or getattr(pl, "render_window", None)
        if rw is not None:
            try:
                # Prefer a simple OpenGL feature level if available
                if hasattr(rw, "SetMultiSamples"):
                    if not _want_quality():
                        rw.SetMultiSamples(0)
            except Exception:
                pass
            try:
                caps = rw.ReportCapabilities()
                vendor = renderer = version = ""
                for line in str(caps).splitlines():
                    low = line.lower()
                    if "vendor" in low and "opengl" in low:
                        vendor = line.strip()
                    if "renderer" in low and "opengl" in low:
                        renderer = line.strip()
                    if "version" in low and "opengl" in low and "glsl" not in low:
                        version = line.strip()
                info = f"{renderer or vendor or 'OpenGL'} | {version}".strip(" |")
            except Exception:
                info = rw.GetClassName()
    except Exception as exc:
        info = f"apply failed: {exc}"
    _LAST_RENDERER = info
    print(f"[gpu_viz] active OpenGL: {info}")
    return info


def field_resolution_for_gpu() -> int:
    """Field mesh resolution. Override: EQMOD_FIELD_RES=48."""
    env = os.environ.get("EQMOD_FIELD_RES", "").strip()
    if env.isdigit():
        return max(24, min(96, int(env)))
    # Safe interactive default (shader-stable + smooth enough)
    return 40


def last_renderer() -> Optional[str]:
    return _LAST_RENDERER


def print_gpu_help() -> None:
    print(
        "[gpu_viz] SAFE OpenGL mode (fixes 'Could not set shader program' on AMD).\n"
        "  Optional quality later: set EQMOD_GL_QUALITY=1\n"
        "  Prefer RX 7700S: Windows → Settings → System → Display → Graphics\n"
        "    → add .venv\\Scripts\\python.exe → High performance"
    )
