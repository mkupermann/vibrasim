"""Pygame renderer. Reads World state; never mutates it."""
from __future__ import annotations
import math
import numpy as np
import pygame

BG_COLOR = (14, 14, 20)
COLOR_VIBR_EVEN = (74, 144, 226)
COLOR_VIBR_ODD = (231, 76, 60)
COLOR_ELECTRON = (243, 156, 18)
COLOR_ATOM = (255, 255, 255)
COLOR_LINE_PAIR = (204, 204, 204, 128)
COLOR_LINE_TRIAD = (220, 220, 220, 200)
COLOR_LINE_ATOM = (255, 240, 200, 255)

WINDOW_SIZE = (1024, 1024)
MARGIN = 12


class Renderer:
    def __init__(self, world):
        self.world = world
        pygame.init()
        pygame.display.set_caption("World of Vibrations")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Menlo,Monaco,Consolas,monospace", 14)
        self.line_surf = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        self._build_atom_halo()
        self.viewport_w = WINDOW_SIZE[0] - 2 * MARGIN
        self.viewport_h = WINDOW_SIZE[1] - 2 * MARGIN
        self.scale_x = self.viewport_w / world.config.box_size[0]
        self.scale_y = self.viewport_h / world.config.box_size[1]
        self.fps = 60.0

    def _build_atom_halo(self) -> None:
        size = 64
        self.halo = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        for y in range(size):
            for x in range(size):
                d = math.hypot(x - cx, y - cy)
                if d > cx:
                    continue
                alpha = max(0, int(180 * (1 - d / cx) ** 2))
                self.halo.set_at((x, y), (255, 220, 160, alpha))

    def world_to_screen(self, pos: np.ndarray) -> tuple[int, int]:
        return (
            int(MARGIN + pos[0] * self.scale_x),
            int(MARGIN + pos[1] * self.scale_y),
        )

    def draw(self) -> None:
        w = self.world
        self.screen.fill(BG_COLOR)
        self.line_surf.fill((0, 0, 0, 0))
        self._draw_lines(w)
        self.screen.blit(self.line_surf, (0, 0))
        self._draw_vibrations(w)
        self._draw_nodes(w)
        self._draw_stats(w)
        pygame.display.flip()
        self.fps = self.clock.get_fps() or self.fps
        self.clock.tick(60)

    def _draw_vibrations(self, w) -> None:
        for i in range(w.s_pos.shape[0]):
            if not w.s_alive[i]:
                continue
            color = COLOR_VIBR_EVEN if w.s_pol[i] else COLOR_VIBR_ODD
            r = max(2, int(math.log10(max(w.s_freq[i], 10.0)) - 1))
            pygame.draw.circle(self.screen, color, self.world_to_screen(w.s_pos[i]), r)

    def _draw_nodes(self, w) -> None:
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            pos = self.world_to_screen(w.k_pos[i])
            if level == 1:
                pygame.draw.circle(self.screen, COLOR_ELECTRON, pos, 5)
            elif level == 4:
                hx, hy = pos
                self.screen.blit(self.halo, (hx - 32, hy - 32),
                                 special_flags=pygame.BLEND_RGBA_ADD)
                pygame.draw.circle(self.screen, COLOR_ATOM, pos, 7)

    def _draw_lines(self, w) -> None:
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            if level not in (2, 3, 4):
                continue
            color = {
                2: COLOR_LINE_PAIR,
                3: COLOR_LINE_TRIAD,
                4: COLOR_LINE_ATOM,
            }[level]
            ground = self._ground_electron_positions(w, i)
            for a in range(len(ground)):
                for b in range(a + 1, len(ground)):
                    pa = self.world_to_screen(ground[a])
                    pb = self.world_to_screen(ground[b])
                    pygame.draw.line(self.line_surf, color, pa, pb, 1)

    def _ground_electron_positions(self, w, i: int) -> list[np.ndarray]:
        """Walk composition one indirection deep to gather electron positions."""
        out: list[np.ndarray] = []
        if int(w.k_comp_kind[i]) == 0:
            return [w.k_pos[i].copy()]
        start = int(w.k_comp_offset[i])
        end = int(w.k_comp_offset[i + 1])
        for j in range(start, end):
            child = int(w.k_comp_indices[j])
            child_level = int(w.k_level[child])
            if child_level == 1:
                out.append(w.k_pos[child].copy())
            else:
                out.extend(self._ground_electron_positions(w, child))
        return out

    def _draw_stats(self, w) -> None:
        n_v = int(w.n_alive)
        n_e = int(np.sum((w.k_level[:w.k_count] == 1) & w.k_alive[:w.k_count]))
        n_p = int(np.sum((w.k_level[:w.k_count] == 2) & w.k_alive[:w.k_count]))
        n_t = int(np.sum((w.k_level[:w.k_count] == 3) & w.k_alive[:w.k_count]))
        n_a = int(np.sum((w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]))
        text = (f"t = {w.t:7.2f} s | FPS {self.fps:4.0f} | "
                f"vibr {n_v:5d} | e- {n_e:4d} | pair {n_p:4d} | "
                f"triad {n_t:4d} | atom {n_a:4d}")
        surf = self.font.render(text, True, (230, 230, 230))
        self.screen.blit(surf, (MARGIN, MARGIN // 2))

    def close(self) -> None:
        pygame.quit()
