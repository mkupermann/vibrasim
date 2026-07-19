"""GPU preferences for PyVista / VTK live visualisation.

Your machine has:
  - AMD Radeon RX 7700S  (discrete, preferred)
  - AMD Radeon 780M      (integrated)

We request the **high-performance** adapter and tune OpenGL MSAA / depth peeling.
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
    os.environ.setdefault("__GL_THREADED_OPTIMIZATIONS", "1")

    if sys.platform != "win32":
        return
    try:
        import winreg

        py = os.path.abspath(sys.executable)
        key_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            # 2 = High performance GPU (RX 7700S on this laptop)
            winreg.SetValueEx(key, py, 0, winreg.REG_SZ, "GpuPreference=2;")
            if py.lower().endswith("python.exe"):
                pyw = py[:-10] + "pythonw.exe"
                if os.path.isfile(pyw):
                    winreg.SetValueEx(key, pyw, 0, winreg.REG_SZ, "GpuPreference=2;")
    except Exception as exc:
        print(f"[gpu_viz] registry GpuPreference skip: {exc}")


def configure_pyvista_gpu(multi_samples=8, verbose=True):
    """Global PyVista theme + once-per-process GPU request."""
    global _CONFIGURED
    request_high_performance_gpu()
    try:
        import pyvista as pv

        pv.global_theme.multi_samples = multi_samples
        pv.global_theme.anti_aliasing = "msaa"
        try:
            pv.global_theme.allow_empty_mesh = True
        except Exception:
            pass
    except Exception as exc:
        print(f"[gpu_viz] pyvista theme: {exc}")
    _CONFIGURED = True
    if verbose:
        print(f"[gpu_viz] high-performance GPU requested for {sys.executable}")


def apply_plotter_gpu(pl) -> str:
    """Tune an existing Plotter for GPU quality. Returns renderer string."""
    global _LAST_RENDERER
    configure_pyvista_gpu(8, False)
    info = "unknown"
    try:
        try:
            pl.enable_anti_aliasing("msaa", multi_samples=8)
        except Exception:
            try:
                pl.enable_anti_aliasing("ssaa")
            except Exception:
                pass
        try:
            pl.enable_depth_peeling(number_of_peels=8, occlusion_ratio=0.0)
        except Exception:
            pass
        rw = getattr(pl, "ren_win", None) or getattr(pl, "render_window", None)
        if rw is not None:
            try:
                rw.SetMultiSamples(8)
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
    """Higher field mesh resolution on discrete GPUs."""
    name = (_LAST_RENDERER or "").lower()
    if any(k in name for k in ("7700", "7800", "7900", "rtx", "gtx", "radeon(tm) rx", "geforce")):
        return 72
    if "780m" in name or "integrated" in name or "uhd" in name:
        return 48
    return 56


def last_renderer() -> Optional[str]:
    return _LAST_RENDERER
