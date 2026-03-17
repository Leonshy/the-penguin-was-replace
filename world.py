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

TREE_REGROW_MS = 20_000   # 20 segundos

# ═══════════════════════════════════════════════════════
#  LAYOUT (21 cols × 14 filas)
#
#   cols:   0-6        7-13        14-20
#   r 0-5:  YERMO      ALMACEN     FABRICA
#   r 6-11: MINA       PESCA       BOSQUE
#   r 12:   COSTA      COSTA       COSTA   (franja de costa)
#   r 13:   MAR        MAR         MAR     (3 bloques de mar abajo)
#
#  Solo la zona PESCA tiene computadora.
# ═══════════════════════════════════════════════════════

def get_zone(row: int, col: int) -> str:
    """Devuelve el tipo de suelo base de la posicion."""
    if row >= 13:
        return "agua"          # mar permanente en la ultima fila
    if row == 12:
        return "f_pesca"       # franja de costa/playa (pisable)
    if col <= 6:
        return "f_yermo" if row <= 5 else "f_mina"
    elif col <= 13:
        return "f_almacen" if row <= 5 else "f_pesca"
    else:
        return "f_fabrica" if row <= 5 else "f_bosque"


TILE_BLOCKERS = {"agua", "arbol", "mina"}

TILE_LABEL: dict[str, tuple[str, tuple]] = {
    "nido":        ("N",   (220, 160,  80)),
    "computadora": ("PC",  (160, 170, 255)),
    "arbol":       ("Y",   ( 90, 200,  90)),
    "mina":        ("#",   (160, 165, 190)),
    "almacen":     ("[]",  (160, 150, 220)),
    "fabrica":     ("FX",  (120, 210, 220)),
    "costa":       ("~",   (100, 230, 230)),
    "agua":        ("~~",  ( 80, 120, 210)),
}

# Posiciones de los arboles en la zona BOSQUE (r6-11, c14-20)
TREE_SPAWN_POSITIONS: list[tuple[int, int]] = [
    (6, 15), (6, 17), (6, 19),
    (7, 15), (7, 18), (7, 20),
    (8, 15), (8, 17), (8, 19),
    (9, 15), (9, 18), (9, 20),
    (10,15), (10,17), (10,19),
    (11,15), (11,17), (11,20),
]


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
#  WORLD
# ═══════════════════════════════════════════════════════
ZONE_NAMES = {
    "f_pesca":   "Costa de Pesca",
    "f_bosque":  "Bosque Glacial",
    "f_mina":    "Mina de Hielo",
    "f_almacen": "Almacen Central",
    "f_fabrica": "Iglu Cyborg",
    "f_yermo":   "Yermo",
    "agua":      "Mar",
    "costa":     "Costa",
}


class World:
    def __init__(self):
        self.grid: list[list[Tile]] = [
            [Tile(get_zone(r, c)) for c in range(WW)]
            for r in range(WH)
        ]
        # Cola de regrowth: (tiempo_ms, row, col)
        self._regrow_queue: list[tuple[float, int, int]] = []
        self._build()

    # ── Construccion del mapa ────────────────────────
    def _build(self):
        g = self.grid

        # ALMACEN interior (r1-4, c8-12)
        for r in range(1, 5):
            for c in range(8, 13):
                g[r][c] = Tile("almacen")

        # FABRICA interior (r1-4, c15-19)
        for r in range(1, 5):
            for c in range(15, 20):
                g[r][c] = Tile("fabrica")

        # MINA (r7-10, c1-5)
        for r in range(7, 11):
            for c in range(1, 6):
                g[r][c] = Tile("mina")

        # PESCA: PC unica en (7, 10)
        g[7][10] = Tile("computadora")

        # COSTA: franja completa en fila 12 (pisable, separa pesca del mar)
        for c in range(WW):
            g[12][c] = Tile("costa")

        # MAR: fila 13 completa — 3 bloques visuales (izq / centro / der)
        # Todos son "agua" pero quedan separados visualmente por los bordes
        for c in range(WW):
            g[13][c] = Tile("agua")

        # BOSQUE: arboles en r6-11, c14-20
        for r, c in TREE_SPAWN_POSITIONS:
            if 0 <= r < WH and 0 <= c < WW:
                g[r][c] = Tile("arbol")

    # ── API ─────────────────────────────────────────
    def set_tile(self, row: int, col: int, tipo: str):
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile(tipo)

    def get_tile(self, row: int, col: int) -> Tile:
        if 0 <= row < WH and 0 <= col < WW:
            return self.grid[row][col]
        return Tile("agua")

    def cut_tree(self, row: int, col: int, current_time_ms: float):
        """Tala el arbol y programa su regrowth en 20 segundos."""
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile(get_zone(row, col))
            self._regrow_queue.append((current_time_ms + TREE_REGROW_MS, row, col))

    def update(self, current_time_ms: float):
        """Llamado cada frame: replanta los arboles cuando llega su tiempo."""
        remaining = []
        for (regrow_at, row, col) in self._regrow_queue:
            if current_time_ms >= regrow_at:
                # Solo replanta si la tile sigue siendo el suelo base
                if self.grid[row][col].tipo == get_zone(row, col):
                    self.grid[row][col] = Tile("arbol")
            else:
                remaining.append((regrow_at, row, col))
        self._regrow_queue = remaining

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
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if ((nr, nc) not in visited
                        and 0 <= nr < WH and 0 <= nc < WW):
                    tile = self.grid[nr][nc]
                    if tile.transitable or (nr, nc) == (tr, tc):
                        visited.add((nr, nc))
                        prev[(nr, nc)] = (r, c)
                        q.append((nr, nc))
        return []

    def build_nido(self, row: int, col: int):
        """Coloca un tile de nido cyborg en la posicion dada."""
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile("nido")

    def zone_name(self, row: int, col: int) -> str:
        if 0 <= row < WH and 0 <= col < WW:
            t = self.grid[row][col].tipo
            if t in ZONE_NAMES:
                return ZONE_NAMES[t]
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