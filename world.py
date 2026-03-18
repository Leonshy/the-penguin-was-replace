# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — world.py
#  Tiles GBA pixel art generados en runtime
# ═══════════════════════════════════════════════════════
from __future__ import annotations
from collections import deque
import pygame
from config import (
    T, WW, WH, VW, VH, HUD_H,
    TILE_COLORS, CUI_WHITE,
)

TREE_REGROW_MS = 20_000

# ── Layout ──────────────────────────────────────────────
def get_zone(row: int, col: int) -> str:
    if row >= 13:   return "agua"
    if row == 12:   return "f_pesca"
    if col <= 6:    return "f_yermo" if row <= 5 else "f_mina"
    elif col <= 13: return "f_almacen" if row <= 5 else "f_pesca"
    else:           return "f_fabrica" if row <= 5 else "f_bosque"

TILE_BLOCKERS = {"agua", "arbol", "mina"}

TILE_LABEL: dict[str, tuple[str, tuple]] = {
    "nido":        ("N",   (220, 160,  80)),
    "computadora": ("PC",  (160, 170, 255)),
    "arbol":       ("♣",   ( 90, 200,  90)),
    "mina":        ("#",   (160, 165, 190)),
    "almacen":     ("[]",  (160, 150, 220)),
    "fabrica":     ("FX",  (120, 210, 220)),
    "costa":       ("~",   (100, 230, 230)),
    "agua":        ("≈",   ( 80, 120, 210)),
}

TREE_SPAWN_POSITIONS: list[tuple[int, int]] = [
    (6,15),(6,17),(6,19),
    (7,15),(7,18),(7,20),
    (8,15),(8,17),(8,19),
    (9,15),(9,18),(9,20),
    (10,15),(10,17),(10,19),
    (11,15),(11,17),(11,20),
]

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


# ═══════════════════════════════════════════════════════
#  GENERADOR DE TILES GBA PIXEL ART
# ═══════════════════════════════════════════════════════
def _px(s, x, y, c):
    s.set_at((x, y), c)

def _rect(s, x, y, w, h, c):
    pygame.draw.rect(s, c, (x, y, w, h))

def _lighten(c, n=30):
    return tuple(min(255, v + n) for v in c)

def _darken(c, n=30):
    return tuple(max(0, v - n) for v in c)

def _make_gba_tile(tipo: str, size: int) -> pygame.Surface:
    """Genera un tile pixel art escalado a `size` px."""
    BASE = 16
    s = pygame.Surface((BASE, BASE))
    _draw_tile_16(s, tipo)
    if size != BASE:
        return pygame.transform.scale(s, (size, size))
    return s

def _draw_tile_16(s: pygame.Surface, tipo: str):
    """Dibuja el tile en un Surface 16×16."""
    B = TILE_COLORS

    if tipo == "agua":
        s.fill((16, 52, 160))
        for y in range(0, 16, 4):
            for x in range(0, 16, 8):
                c = (32, 80, 192) if (y // 4 + x // 8) % 2 == 0 else (24, 64, 176)
                pygame.draw.line(s, c, (x, y+1), (x+5, y+1))
        # brillos
        for px, py in [(2,2),(10,6),(4,10),(12,14)]:
            s.set_at((px, py), (80, 160, 255))
            s.set_at((px+1, py), (64, 140, 240))

    elif tipo == "f_pesca":
        s.fill((8, 28, 56))
        for y in range(0, 16, 4):
            c = (14, 40, 72) if y % 8 == 0 else (10, 32, 60)
            pygame.draw.line(s, c, (0, y+2), (15, y+2))

    elif tipo == "costa":
        # Mitad agua arriba, arena/hielo abajo
        _rect(s, 0, 0, 16, 8, (8, 64, 152))
        _rect(s, 0, 8, 16, 8, (176, 220, 220))
        # olas
        for x in range(0, 16, 4):
            s.set_at((x, 6), (48, 120, 200))
            s.set_at((x+2, 7), (64, 144, 216))
        # espuma
        for x in range(0, 16, 3):
            s.set_at((x, 8), (220, 248, 248))
        # granos de arena/hielo
        for px, py in [(2,10),(6,12),(10,11),(14,13),(4,14),(8,10),(12,13)]:
            s.set_at((px, py), (200, 236, 236))

    elif tipo == "arbol":
        s.fill((16, 48, 16))
        # Copa 3 tonos de verde
        copa = [
            "   ####   ",
            "  ######  ",
            " ######## ",
            "##########",
            " ######## ",
            "  ######  ",
        ]
        cols = [(32, 128, 32), (48, 160, 48), (24, 104, 24), (56, 176, 56)]
        for ri, row in enumerate(copa):
            for ci, ch in enumerate(row):
                if ch == '#':
                    idx = (ri + ci) % len(cols)
                    s.set_at((ci + 3, ri + 2), cols[idx])
        # borde oscuro copa
        for ci, ch in enumerate("##########"):
            s.set_at((ci+3, 2), (16, 80, 16))
        # tronco
        _rect(s, 7, 9, 2, 6, (88, 56, 24))
        s.set_at((7, 9), (112, 72, 32))
        s.set_at((7, 10), (104, 64, 28))
        # raices
        s.set_at((6, 14), (72, 44, 16))
        s.set_at((9, 14), (72, 44, 16))

    elif tipo == "f_bosque":
        s.fill((8, 36, 12))
        dots = [(1,1),(4,0),(8,2),(12,1),(15,3),(2,5),(6,4),(10,6),(14,5),(3,9),(7,8),(11,10),(15,8),(1,12),(5,11),(9,13),(13,12)]
        for dx, dy in dots:
            _rect(s, dx, dy, 2, 2, (20, 72, 20))

    elif tipo == "mina":
        s.fill((56, 60, 88))
        # Paredes de roca
        _rect(s, 0, 0, 16, 3, (72, 76, 112))
        _rect(s, 0, 13, 16, 3, (40, 44, 64))
        # Grietas
        pygame.draw.line(s, (32, 32, 52), (3, 3), (5, 8))
        pygame.draw.line(s, (32, 32, 52), (11, 4), (9, 9))
        # Cristales de hielo (brillantes)
        for bx, by in [(4, 5), (10, 6), (7, 10)]:
            pygame.draw.polygon(s, (160, 200, 240),
                [(bx,by),(bx+2,by-2),(bx+3,by+1),(bx+1,by+3)])
            pygame.draw.polygon(s, (200, 230, 255),
                [(bx,by),(bx+1,by-1),(bx+2,by+1)])
            s.set_at((bx, by-1), (230, 248, 255))

    elif tipo == "f_mina":
        s.fill((24, 24, 40))
        for y in range(0, 16, 4):
            for x in range(0, 16, 4):
                c = (32, 32, 52) if (x+y)%8==0 else (20, 20, 36)
                _rect(s, x, y, 4, 4, c)

    elif tipo == "almacen":
        s.fill((48, 40, 96))
        # Edificio
        _rect(s, 1, 4, 14, 10, (68, 60, 120))
        _rect(s, 1, 4, 14, 2, (88, 80, 144))  # techo
        _rect(s, 0, 3, 16, 1, (100, 92, 160))  # cornisa
        # Puerta
        _rect(s, 6, 9, 4, 5, (28, 20, 64))
        _rect(s, 6, 9, 4, 1, (40, 32, 80))
        # Ventanas
        _rect(s, 2, 6, 3, 3, (180, 200, 255))
        _rect(s, 2, 6, 3, 1, (200, 220, 255))
        _rect(s, 11, 6, 3, 3, (180, 200, 255))
        _rect(s, 11, 6, 3, 1, (200, 220, 255))
        # Cruz de ventana
        s.set_at((3, 7), (120, 140, 200))
        s.set_at((12, 7), (120, 140, 200))

    elif tipo == "f_almacen":
        s.fill((20, 14, 48))
        for y in range(0, 16, 4):
            for x in range(0, 16, 4):
                c = (28, 22, 60) if (x+y)%8==0 else (16, 10, 40)
                _rect(s, x, y, 4, 4, c)

    elif tipo == "fabrica":
        s.fill((24, 96, 112))
        # Cuerpo
        _rect(s, 0, 6, 16, 10, (36, 112, 128))
        _rect(s, 0, 6, 16, 2, (56, 136, 152))
        # Chimeneas
        _rect(s, 2, 1, 3, 7, (44, 60, 72))
        _rect(s, 8, 2, 3, 6, (44, 60, 72))
        # Vapor (pixeles en tope de chimenea)
        s.set_at((3, 0), (200, 240, 248))
        s.set_at((2, 1), (180, 224, 240))
        s.set_at((9, 1), (200, 240, 248))
        s.set_at((10, 2), (180, 224, 240))
        # Ventana
        _rect(s, 6, 8, 4, 4, (144, 216, 232))
        _rect(s, 6, 8, 4, 1, (180, 240, 248))
        s.set_at((7, 10), (100, 180, 200))

    elif tipo == "f_fabrica":
        s.fill((8, 36, 44))
        for y in range(0, 16, 4):
            for x in range(0, 16, 4):
                c = (16, 48, 56) if (x+y)%8==0 else (8, 32, 40)
                _rect(s, x, y, 4, 4, c)

    elif tipo == "computadora":
        s.fill((32, 40, 160))
        # Monitor
        _rect(s, 1, 1, 14, 10, (56, 72, 200))
        _rect(s, 2, 2, 12, 8, (8, 16, 64))
        # Texto en pantalla (lineas verdes)
        for row in range(3):
            pygame.draw.line(s, (0, 232, 80), (3, 4+row*2), (8+row%2, 4+row*2))
        # Base / cuello
        _rect(s, 6, 11, 4, 2, (80, 88, 128))
        _rect(s, 4, 13, 8, 2, (64, 72, 112))
        # LEDs laterales
        s.set_at((13, 2), (0, 255, 128))
        s.set_at((13, 4), (255, 80, 80))
        s.set_at((13, 6), (255, 200, 0))
        # Cursor parpadeante (pixeles blancos)
        _rect(s, 9, 4, 2, 2, (200, 220, 255))

    elif tipo == "nido":
        s.fill((80, 44, 12))
        # Nido ovalado
        pygame.draw.ellipse(s, (104, 60, 20), (1, 4, 14, 10))
        pygame.draw.ellipse(s, (128, 80, 36), (2, 5, 12, 8))
        pygame.draw.ellipse(s, (60, 28, 8), (5, 7, 6, 5))
        # Paja/ramas
        for i in range(4):
            pygame.draw.line(s, (152, 112, 48), (1+i*3, 8), (3+i*3, 6))
        # Detalles metálicos cyborg
        pygame.draw.line(s, (140, 180, 220), (4, 9), (6, 7))
        pygame.draw.line(s, (140, 180, 220), (10, 9), (12, 7))

    elif tipo == "f_yermo":
        s.fill((18, 18, 26))
        for y in range(0, 16, 4):
            for x in range(0, 16, 4):
                c = (26, 26, 36) if (x+y)%8==0 else (14, 14, 22)
                _rect(s, x, y, 4, 4, c)

    else:
        s.fill(TILE_COLORS.get(tipo, (22, 22, 28)))


# ── Cache de tiles ───────────────────────────────────────
_tile_cache: dict[str, pygame.Surface] = {}

def get_tile_surface(tipo: str, size: int) -> pygame.Surface:
    key = (tipo, size)
    if key not in _tile_cache:
        _tile_cache[key] = _make_gba_tile(tipo, size)
    return _tile_cache[key]

def clear_tile_cache():
    _tile_cache.clear()


# ═══════════════════════════════════════════════════════
#  TILE DATA
# ═══════════════════════════════════════════════════════
class Tile:
    __slots__ = ("tipo", "color", "transitable")

    def __init__(self, tipo: str = "f_yermo"):
        self.tipo        = tipo
        self.color       = TILE_COLORS.get(tipo, (22, 22, 28))
        self.transitable = tipo not in TILE_BLOCKERS

    def draw(self, surface: pygame.Surface, x: int, y: int,
             font: pygame.font.Font, tile_size: int = T):
        surf = get_tile_surface(self.tipo, tile_size)
        surface.blit(surf, (x, y))
        # Borde sutil
        border = tuple(max(0, c - 18) for c in self.color)
        pygame.draw.rect(surface, border, (x, y, tile_size, tile_size), 1)
        # Label encima (solo si el tile lo tiene)
        info = TILE_LABEL.get(self.tipo)
        if info:
            s = font.render(info[0], True, info[1])
            rect = pygame.Rect(x, y, tile_size, tile_size)
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


# ── Matriz de la fabrica ────────────────────────────────
# La zona fabrica ocupa r0-5, c14-20 en el mundo.
# La cuadricula construible es 5 columnas x 4 filas:
#   col de juego 0-4  → world_col = 15 + col_juego
#   fila de juego 0-3 → world_row =  1 + fila_juego
FACTORY_COLS  = 5   # columnas de la matriz (0..4)
FACTORY_ROWS  = 4   # filas de la matriz (0..3)
FACTORY_WC0   = 15  # primera columna world de la cuadricula
FACTORY_WR0   = 1   # primera fila world de la cuadricula


class World:
    def __init__(self):
        self.grid: list[list[Tile]] = [
            [Tile(get_zone(r, c)) for c in range(WW)]
            for r in range(WH)
        ]
        self._regrow_queue: list[tuple[float, int, int]] = []
        self._build()

    def _build(self):
        g = self.grid
        for r in range(1, 5):
            for c in range(8, 13):
                g[r][c] = Tile("almacen")

        # FABRICA: zona vacia — el jugador construye nidos con construir_nido(x, y)
        # Matriz 5x4: columnas 0-4 → world c15-19, filas 0-3 → world r1-4
        # (no se colocan tiles fabrica aqui, el suelo es f_fabrica)

        # MINA (r7-10, c1-5)
        for r in range(7, 11):
            for c in range(1, 6):
                g[r][c] = Tile("mina")
        g[7][10] = Tile("computadora")
        for c in range(WW):
            g[12][c] = Tile("costa")
        for c in range(WW):
            g[13][c] = Tile("agua")
        for r, c in TREE_SPAWN_POSITIONS:
            if 0 <= r < WH and 0 <= c < WW:
                g[r][c] = Tile("arbol")

    def set_tile(self, row, col, tipo):
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile(tipo)

    def get_tile(self, row, col) -> Tile:
        if 0 <= row < WH and 0 <= col < WW:
            return self.grid[row][col]
        return Tile("agua")

    def cut_tree(self, row, col, current_time_ms):
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile(get_zone(row, col))
            self._regrow_queue.append((current_time_ms + TREE_REGROW_MS, row, col))

    def update(self, current_time_ms):
        remaining = []
        for (regrow_at, row, col) in self._regrow_queue:
            if current_time_ms >= regrow_at:
                if self.grid[row][col].tipo == get_zone(row, col):
                    self.grid[row][col] = Tile("arbol")
            else:
                remaining.append((regrow_at, row, col))
        self._regrow_queue = remaining

    def find_nearest(self, fr, fc, tipo):
        best, bd = None, float("inf")
        for r in range(WH):
            for c in range(WW):
                if self.grid[r][c].tipo == tipo:
                    d = abs(r - fr) + abs(c - fc)
                    if d < bd:
                        best, bd = (r, c), d
        return best

    def pathfind(self, fr, fc, tr, tc):
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
                nr, nc = r+dr, c+dc
                if ((nr,nc) not in visited
                        and 0 <= nr < WH and 0 <= nc < WW):
                    tile = self.grid[nr][nc]
                    if tile.transitable or (nr,nc) == (tr,tc):
                        visited.add((nr,nc))
                        prev[(nr,nc)] = (r,c)
                        q.append((nr,nc))
        return []

    def build_nido(self, row: int, col: int):
        """Coloca un tile de nido en coordenadas world (uso interno)."""
        if 0 <= row < WH and 0 <= col < WW:
            self.grid[row][col] = Tile("nido")

    def place_nido(self, mx: int, my: int) -> str:
        """
        Coloca un nido en la posicion de la MATRIZ de la fabrica.
        mx = columna de la matriz (0 .. FACTORY_COLS-1)
        my = fila    de la matriz (0 .. FACTORY_ROWS-1)
        Devuelve "ok" o un mensaje de error.
        """
        if not (0 <= mx < FACTORY_COLS):
            return (f"Columna {mx} fuera de rango. "
                    f"Usa 0 a {FACTORY_COLS-1}.")
        if not (0 <= my < FACTORY_ROWS):
            return (f"Fila {my} fuera de rango. "
                    f"Usa 0 a {FACTORY_ROWS-1}.")
        wr = FACTORY_WR0 + my
        wc = FACTORY_WC0 + mx
        tile = self.grid[wr][wc]
        if tile.tipo == "nido":
            return f"La celda ({mx}, {my}) ya tiene un nido."
        self.grid[wr][wc] = Tile("nido")
        return "ok"

    def factory_cell_world(self, mx: int, my: int) -> tuple[int, int]:
        """Convierte coordenadas de matriz a coordenadas world."""
        return (FACTORY_WR0 + my, FACTORY_WC0 + mx)

    def zone_name(self, row: int, col: int) -> str:
        if 0 <= row < WH and 0 <= col < WW:
            t = self.grid[row][col].tipo
            if t in ZONE_NAMES:
                return ZONE_NAMES[t]
        return ZONE_NAMES.get(get_zone(row, col), "?")

    def draw(self, surface, cam_col, cam_row, font,
             tile_size=None, vw=None, vh=None):
        ts  = tile_size or T
        _vw = vw or VW
        _vh = vh or VH
        for vr in range(_vh):
            for vc in range(_vw):
                wr, wc = cam_row + vr, cam_col + vc
                if 0 <= wr < WH and 0 <= wc < WW:
                    self.grid[wr][wc].draw(
                        surface,
                        vc * ts,
                        vr * ts + HUD_H,
                        font,
                        ts,
                    )
