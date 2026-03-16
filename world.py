# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — world.py
# ═══════════════════════════════════════════════════════
from __future__ import annotations
from collections import deque

import pygame

from config import (
    T, WW, WH, VW, VH, HUD_H,
    TILE_COLORS, CUI_WHITE,
)


# ── Helpers de zona ─────────────────────────────────────
def get_zone(row: int, col: int) -> str:
    if row <= 6:
        if col <= 6:  return "f_pesca"
        if col <= 13: return "f_bosque"
        return "f_mina"
    else:
        if col <= 6:  return "f_almacen"
        if col <= 13: return "f_fabrica"
        return "f_yermo"


TILE_BLOCKERS = {"agua", "arbol", "mina"}

TILE_LABEL: dict[str, tuple[str, tuple]] = {
    "computadora": ("PC",  (160, 170, 255)),
    "arbol":       ("Y",   ( 90, 200,  90)),
    "mina":        ("#",   (160, 165, 190)),
    "almacen":     ("[]",  (160, 150, 220)),
    "fabrica":     ("FX",  (120, 210, 220)),
    "costa":       ("~",   (100, 230, 230)),
    "agua":        ("~~",  ( 80, 120, 210)),
}


# ═══════════════════════════════════════════════════════
#  TILE
# ═══════════════════════════════════════════════════════
class Tile:
    __slots__ = ("tipo", "color", "transitable")

    def __init__(self, tipo: str = "f_yermo"):
        self.tipo        = tipo
        self.color       = TILE_COLORS.get(tipo, (22, 22, 28))
        self.transitable = tipo not in TILE_BLOCKERS

    def draw(self, surface: pygame.Surface,
             x: int, y: int, font: pygame.font.Font):
        rect = pygame.Rect(x, y, T, T)
        pygame.draw.rect(surface, self.color, rect)
        border = tuple(max(0, c - 20) for c in self.color)
        pygame.draw.rect(surface, border, rect, 1)
        info = TILE_LABEL.get(self.tipo)
        if info:
            s = font.render(info[0], True, info[1])
            surface.blit(s, s.get_rect(center=rect.center))

    def __repr__(self):
        return f"Tile({self.tipo})"


# ═══════════════════════════════════════════════════════
#  WORLD  –  Grid unico WW × WH con 5 zonas
# ═══════════════════════════════════════════════════════
ZONE_NAMES = {
    "f_pesca":   "Costa de Pesca",
    "f_bosque":  "Bosque Glacial",
    "f_mina":    "Mina de Hielo",
    "f_almacen": "Almacen Central",
    "f_fabrica": "Iglu Cyborg",
    "f_yermo":   "Yermo",
}


class World:
    def __init__(self):
        self.grid: list[list[Tile]] = [
            [Tile(get_zone(r, c)) for c in range(WW)]
            for r in range(WH)
        ]
        self._build()

    # ── Construccion del mapa ────────────────────────
    def _build(self):
        g = self.grid

        # PESCA (r0-6, c0-6)
        for r in range(7):
            g[r][5] = Tile("agua")
            g[r][6] = Tile("agua")
        for r in range(1, 6):
            g[r][4] = Tile("costa")
        g[3][3] = Tile("computadora")

        # BOSQUE (r0-6, c7-13)
        for r, c in [(1,8),(1,10),(1,12),(2,8),(2,11),(2,13),
                     (3,8),(3,12),(4,9),(4,11),(5,8),(5,10),(5,12)]:
            g[r][c] = Tile("arbol")
        g[3][10] = Tile("computadora")

        # MINA (r0-6, c14-20)
        for r in range(1, 6):
            for c in range(15, 20):
                g[r][c] = Tile("mina")
        g[3][17] = Tile("computadora")

        # ALMACEN (r7-13, c0-6)
        for r in range(8, 13):
            for c in range(1, 6):
                g[r][c] = Tile("almacen")
        g[10][3] = Tile("computadora")

        # FABRICA (r7-13, c7-13)
        for r in range(8, 13):
            for c in range(8, 13):
                g[r][c] = Tile("fabrica")
        g[10][10] = Tile("computadora")

    # ── API ─────────────────────────────────────────
    def set_tile(self, row: int, col: int, tipo: str):
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile(tipo)

    def get_tile(self, row: int, col: int) -> Tile:
        if 0 <= row < WH and 0 <= col < WW:
            return self.grid[row][col]
        return Tile("agua")

    def find_nearest(self, fr: int, fc: int, tipo: str) -> tuple[int, int] | None:
        best, bd = None, float("inf")
        for r in range(WH):
            for c in range(WW):
                if self.grid[r][c].tipo == tipo:
                    d = abs(r - fr) + abs(c - fc)
                    if d < bd:
                        best, bd = (r, c), d
        return best

    def pathfind(self, fr: int, fc: int,
                 tr: int, tc: int) -> list[tuple[int, int]]:
        """BFS. Devuelve lista de pasos sin incluir el inicio."""
        if (fr, fc) == (tr, tc):
            return []
        visited = {(fr, fc)}
        prev    = {(fr, fc): None}
        q       = deque([(fr, fc)])
        while q:
            r, c = q.popleft()
            if (r, c) == (tr, tc):
                path, cur = [], (tr, tc)
                while prev[cur] is not None:
                    path.append(cur)
                    cur = prev[cur]
                path.reverse()
                return path
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr, nc = r + dr, c + dc
                if ((nr, nc) not in visited
                        and 0 <= nr < WH and 0 <= nc < WW):
                    tile = self.grid[nr][nc]
                    if tile.transitable or (nr, nc) == (tr, tc):
                        visited.add((nr, nc))
                        prev[(nr, nc)] = (r, c)
                        q.append((nr, nc))
        return []

    def zone_name(self, row: int, col: int) -> str:
        return ZONE_NAMES.get(get_zone(row, col), "?")

    # ── Render ──────────────────────────────────────
    def draw(self, surface: pygame.Surface,
             cam_col: int, cam_row: int,
             font: pygame.font.Font):
        for vr in range(VH):
            for vc in range(VW):
                wr, wc = cam_row + vr, cam_col + vc
                if 0 <= wr < WH and 0 <= wc < WW:
                    self.grid[wr][wc].draw(
                        surface,
                        vc * T,
                        vr * T + HUD_H,
                        font,
                    )
