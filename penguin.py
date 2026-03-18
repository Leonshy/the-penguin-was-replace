# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — penguin.py  (sprites GBA mejorados)
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import threading
import random
import pygame

from config import (
    PENGUIN_COLORS, MOVE_DELAY, ACTION_DELAY,
    T, HUD_H, VW, VH, CUI_BLACK, CUI_WHITE, CUI_ORANGE,
    NIDO_COST_MADERA, NIDO_COST_HIELO,
    FISH_PROBABILITY,
)
from world import World, get_zone
from inventory import Inventory

PERSONAL_MAX = 5


class ScriptStopped(Exception):
    pass


# ═══════════════════════════════════════════════════════
#  INTERPRETE (sin cambios)
# ═══════════════════════════════════════════════════════
class CommandInterpreter:
    def __init__(self, penguin):
        self.penguin = penguin
        self.out: list[tuple[str, str]] = []

    def log(self, *args):
        msg = " ".join(str(a) for a in args)
        self.out.append((msg, "ok"))
        p = self.penguin
        if p.win and p.win.active:
            p.win.out = list(self.out)

    def build_ns(self) -> dict:
        p = self.penguin
        safe = {
            "range": range, "len": len, "int": int, "str": str,
            "float": float, "bool": bool, "list": list, "tuple": tuple,
            "abs": abs, "max": max, "min": min, "round": round,
            "isinstance": isinstance, "enumerate": enumerate,
            "zip": zip, "sorted": sorted, "sum": sum,
            "any": any, "all": all, "print": self.log,
            "True": True, "False": False, "None": None,
            "Exception": Exception, "TypeError": TypeError,
            "ValueError": ValueError, "NameError": NameError,
            "StopIteration": StopIteration,
            "__build_class__": __build_class__,
            "__name__": "<pinguino>",
        }
        return {
            "__builtins__": safe,
            "pescar":           p.cmd_pescar,
            "talar":            p.cmd_talar,
            "picar_hielo":      p.cmd_picar_hielo,
            "almacenar":        p.cmd_almacenar,
            "construir_nido":   p.cmd_construir_nido,
            "crear_pinguino":   p.cmd_crear_pinguino,
            "inventario_lleno": p.inventario_lleno,
            "inventario":       p.personal_inv,
        }

    def run(self, code: str):
        self.out.clear()
        p = self.penguin
        p._stop_event.set()
        if p._script_thread and p._script_thread.is_alive():
            p._script_thread.join(timeout=0.5)
        p._stop_event.clear()
        p._action_queue.clear()

        def _body():
            ns = self.build_ns()
            try:
                exec(compile(code, "<pinguino>", "exec"), ns)
            except ScriptStopped:
                self.out.append(("Script detenido.", "ok"))
            except SystemExit:
                self.out.append(("No podes llamar exit().", "err"))
            except Exception as e:
                self.out.append((f"ERROR {type(e).__name__}: {e}", "err"))
            finally:
                if p.win and p.win.active:
                    p.win.out = list(self.out)
                    p.win.running = False

        p._script_thread = threading.Thread(target=_body, daemon=True)
        p._script_thread.start()
        return []


# ═══════════════════════════════════════════════════════
#  SPRITE GENERATOR GBA
# ═══════════════════════════════════════════════════════
def _make_penguin_surface(color: tuple, size: int = 16) -> pygame.Surface:
    """Genera un sprite de pingüino cyborg 16x16 pixel art."""
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))

    body   = color
    belly  = (240, 240, 248)
    dark   = tuple(max(0, c - 70) for c in color)
    bright = tuple(min(255, c + 60) for c in color)
    eye    = (248, 248, 24)
    beak   = (248, 168, 48)

    # Cuerpo
    pygame.draw.ellipse(s, body, (3, 4, 10, 11))
    # Panza
    pygame.draw.ellipse(s, belly, (5, 6, 6, 8))
    # Cabeza
    pygame.draw.ellipse(s, body, (4, 1, 8, 7))
    # Brillo cabeza
    s.set_at((6, 2), bright)
    s.set_at((7, 2), bright)
    # Ojos
    pygame.draw.rect(s, eye, (5, 3, 2, 2))
    pygame.draw.rect(s, eye, (9, 3, 2, 2))
    s.set_at((6, 3), (0, 0, 0))
    s.set_at((10, 3), (0, 0, 0))
    # Pico
    pygame.draw.rect(s, beak, (7, 6, 2, 2))
    s.set_at((7, 6), (255, 200, 80))
    # Aletas
    pygame.draw.ellipse(s, dark, (1, 5, 3, 6))
    pygame.draw.ellipse(s, dark, (12, 5, 3, 6))
    # Pies
    pygame.draw.rect(s, beak, (4, 14, 3, 2))
    pygame.draw.rect(s, beak, (9, 14, 3, 2))
    s.set_at((4, 14), (255, 200, 80))
    s.set_at((9, 14), (255, 200, 80))
    # Antena cyborg
    pygame.draw.line(s, (120, 200, 255), (8, 1), (11, 0))
    pygame.draw.rect(s, (0, 240, 255), (11, 0, 2, 2))
    s.set_at((12, 0), (255, 255, 255))

    if size != 16:
        return pygame.transform.scale(s, (size, size))
    return s


def _make_selection_ring(color: tuple, size: int) -> pygame.Surface:
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    c = (*color, 160)
    # Anillo animado (sombra + anillo principal)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (4, size-10, size-8, 8))
    pygame.draw.ellipse(s, c, (3, size-11, size-6, 8), 2)
    return s


# ═══════════════════════════════════════════════════════
#  PINGUINO
# ═══════════════════════════════════════════════════════
_counter_lock = threading.Lock()


class Penguin:
    _global_counter = 0

    def __init__(self, nombre=None, row=7, col=9,
                 world=None, inventory=None, colony=None):
        with _counter_lock:
            Penguin._global_counter += 1
            idx = Penguin._global_counter
        self.nombre    = nombre or f"Pingu-{idx:02d}"
        self.row       = row
        self.col       = col
        self.world     = world
        self.inventory = inventory
        self.colony    = colony
        self.interp    = CommandInterpreter(self)
        self.win       = None
        self.selected  = False
        self._wants_new = False
        self.progress = None   # set by Game._spawn
        self.alive     = True
        self.color     = PENGUIN_COLORS[(idx - 1) % len(PENGUIN_COLORS)]

        self.personal_inv: dict[str, int] = {"Pez": 0, "Madera": 0, "Hielo": 0}

        self._stop_event    = threading.Event()
        self._script_thread = None
        self._action_queue  = []
        self._move_timer    = 0
        self._action_lock   = threading.Lock()

        # Caché de sprites por tile_size — se genera bajo demanda
        self._sprite_cache:      dict[int, pygame.Surface] = {}
        self._sprite_walk_cache: dict[int, pygame.Surface] = {}
        self._sel_ring_cache:    dict[int, pygame.Surface] = {}

        # Animación (frame alterno al caminar)
        self._anim_frame  = 0
        self._anim_timer  = 0

    # ── Sprites por tamaño ──────────────────────────────
    def _get_sprites(self, tile_size: int):
        """Devuelve (sprite, sprite_walk, sel_ring) para el tile_size dado.
        Genera y cachea la primera vez que se pide ese tamaño."""
        if tile_size not in self._sprite_cache:
            sz = max(tile_size - 4, 12)
            self._sprite_cache[tile_size]      = _make_penguin_surface(self.color, sz)
            self._sprite_walk_cache[tile_size] = _make_penguin_surface(
                tuple(min(255, c + 20) for c in self.color), sz)
            self._sel_ring_cache[tile_size]    = _make_selection_ring(self.color, tile_size)
        return (self._sprite_cache[tile_size],
                self._sprite_walk_cache[tile_size],
                self._sel_ring_cache[tile_size])

    # ── Helpers ─────────────────────────────────────────
    def inventario_lleno(self, material: str) -> bool:
        return self.personal_inv.get(material, 0) >= PERSONAL_MAX

    def inv_status(self) -> str:
        return "  ".join(f"{k}:{v}/{PERSONAL_MAX}" for k, v in self.personal_inv.items())

    # ── Tick ────────────────────────────────────────────
    def tick(self):
        with self._action_lock:
            if not self._action_queue:
                self._anim_frame = 0
                return
            self._move_timer += 1
            # Animación de caminar
            self._anim_timer += 1
            if self._anim_timer >= 4:
                self._anim_timer = 0
                self._anim_frame ^= 1
            if self._move_timer < MOVE_DELAY:
                return
            self._move_timer = 0
            entry = self._action_queue[0]
            if entry["path"]:
                self.row, self.col = entry["path"].pop(0)
                return
            if entry.get("delay", 0) > 0:
                entry["delay"] -= 1
                return
            action = entry.get("action")
            if action:
                try:
                    action()
                except Exception as e:
                    self.interp.out.append((f"ERROR: {e}", "err"))
                    if self.win and self.win.active:
                        self.win.out = list(self.interp.out)
            done = entry.get("done")
            if done:
                done.set()
            self._action_queue.pop(0)

    def stop_script(self):
        self._stop_event.set()
        with self._action_lock:
            for e in self._action_queue:
                d = e.get("done")
                if d: d.set()
            self._action_queue.clear()

    def _enqueue_and_wait(self, target_tipo, action):
        if self._stop_event.is_set():
            raise ScriptStopped()
        t = self.world.find_nearest(*self._queue_end_pos(), target_tipo)
        if t is None:
            self.interp.log(f"No hay '{target_tipo}' en el mapa.")
            return
        with self._action_lock:
            start = self._queue_end_pos()
            path  = self.world.pathfind(start[0], start[1], t[0], t[1])
            done  = threading.Event()
            self._action_queue.append({
                "path": path, "action": action,
                "done": done, "dest": t, "delay": ACTION_DELAY,
            })
        while not done.wait(timeout=0.05):
            if self._stop_event.is_set():
                raise ScriptStopped()

    def _queue_end_pos(self):
        if self._action_queue:
            d = self._action_queue[-1].get("dest")
            if d: return d
        return (self.row, self.col)

    # ── Comandos ────────────────────────────────────────
    def cmd_pescar(self):
        def _do():
            if self.personal_inv["Pez"] >= PERSONAL_MAX:
                self.interp.log(
                    f"Mochila llena ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                    "Usá almacenar('Pez') primero.")
                return
            if random.random() < FISH_PROBABILITY:
                self.personal_inv["Pez"] += 1
                n = self.personal_inv["Pez"]
                self.interp.log(
                    f"Pescado! Pez: {n}/{PERSONAL_MAX}"
                    + (" — LLENO!" if n >= PERSONAL_MAX else ""))
                # Notificar progreso
                if hasattr(self, "progress") and self.progress:
                    self.progress.on_fish_caught()
                if hasattr(self, "sound") and self.sound:
                    self.sound.play_sfx("pescar")
            else:
                self.interp.log("Se escapo el pez... (60% de falla)")
        self._enqueue_and_wait("costa", _do)

    def cmd_talar(self):
        t = self.world.find_nearest(*self._queue_end_pos(), "arbol")
        if t is None:
            self.interp.log("No hay arboles disponibles."); return
        def _do():
            if self.personal_inv["Madera"] >= PERSONAL_MAX:
                self.interp.log(
                    f"Mochila llena ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                    "Usá almacenar('Madera') primero.")
                return
            pos = (self.row, self.col)
            if self.world.get_tile(*pos).tipo == "arbol":
                self.world.cut_tree(pos[0], pos[1], pygame.time.get_ticks())
            self.personal_inv["Madera"] += 1
            n = self.personal_inv["Madera"]
            self.interp.log(f"Arbol talado! Regrowth 20s. Madera: {n}/{PERSONAL_MAX}" + (" — LLENO!" if n >= PERSONAL_MAX else ""))
            if hasattr(self, "sound") and self.sound:
                self.sound.play_sfx("talar")
        with self._action_lock:
            start = self._queue_end_pos()
            path  = self.world.pathfind(start[0], start[1], t[0], t[1])
            done  = threading.Event()
            self._action_queue.append({"path": path, "action": _do, "done": done, "dest": t, "delay": ACTION_DELAY})
        while not done.wait(timeout=0.05):
            if self._stop_event.is_set():
                raise ScriptStopped()

    def cmd_picar_hielo(self):
        def _do():
            if self.personal_inv["Hielo"] >= PERSONAL_MAX:
                self.interp.log(
                    f"Mochila llena ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                    "Usá almacenar('Hielo') primero.")
                return
            self.personal_inv["Hielo"] += 1
            n = self.personal_inv["Hielo"]
            self.interp.log(f"Hielo extraido! Hielo: {n}/{PERSONAL_MAX}" + (" — LLENO!" if n >= PERSONAL_MAX else ""))
            if hasattr(self, "sound") and self.sound:
                self.sound.play_sfx("picar")
        self._enqueue_and_wait("mina", _do)

    def cmd_almacenar(self, material: str):
        if material not in self.personal_inv:
            self.interp.log(f"'{material}' no existe. Usa 'Pez', 'Madera' o 'Hielo'.")
            return
        if self.personal_inv[material] == 0:
            self.interp.log(f"No tienes {material} para almacenar.")
            return
        def _do():
            qty    = self.personal_inv[material]
            stored = self.inventory.agregar(material, qty)
            self.personal_inv[material] = 0
            total  = self.inventory.obtener(material)
            self.interp.log(f"Almacenado {stored} {material}. Almacen: {total}/500")
        self._enqueue_and_wait("almacen", _do)

    def cmd_construir_nido(self, mx: int = 0, my: int = 0):
        """
        Construye un nido en la MATRIZ de la fabrica.
        Parametros:
          mx = columna (0-4)
          my = fila    (0-3)
        Costo: 50 Madera + 100 Hielo del almacen global.

        Ejemplo: construir_nido(0, 0)  -> celda (col=0, fila=0)
                 construir_nido(2, 1)  -> celda (col=2, fila=1)
        """
        # Validar rango antes de moverse
        from world import FACTORY_COLS, FACTORY_ROWS
        if not (0 <= mx < FACTORY_COLS):
            self.interp.log(
                f"ERROR: columna {mx} fuera de rango. "
                f"Usa 0 a {FACTORY_COLS - 1}.")
            return
        if not (0 <= my < FACTORY_ROWS):
            self.interp.log(
                f"ERROR: fila {my} fuera de rango. "
                f"Usa 0 a {FACTORY_ROWS - 1}.")
            return
        # Verificar recursos
        if self.inventory.obtener("Madera") < NIDO_COST_MADERA:
            self.interp.log(
                f"Necesitas {NIDO_COST_MADERA} Madera "
                f"(tienes {self.inventory.obtener('Madera')}).")
            return
        if self.inventory.obtener("Hielo") < NIDO_COST_HIELO:
            self.interp.log(
                f"Necesitas {NIDO_COST_HIELO} Hielo "
                f"(tienes {self.inventory.obtener('Hielo')}).")
            return
        # Navegar a la celda exacta de la matriz
        wr, wc = self.world.factory_cell_world(mx, my)
        def _do():
            result = self.world.place_nido(mx, my)
            if result != "ok":
                self.interp.log(f"No se pudo construir: {result}")
                return
            if (self.inventory.obtener("Madera") < NIDO_COST_MADERA or
                    self.inventory.obtener("Hielo") < NIDO_COST_HIELO):
                self.interp.log("Recursos insuficientes al llegar.")
                return
            self.inventory.consumir("Madera", NIDO_COST_MADERA)
            self.inventory.consumir("Hielo",  NIDO_COST_HIELO)
            if self.colony:
                self.colony.nidos += 1
            self.interp.log(
                f"Nido construido en ({mx}, {my})! "
                f"(-{NIDO_COST_MADERA} Madera, -{NIDO_COST_HIELO} Hielo)")
            if hasattr(self, "sound") and self.sound:
                self.sound.play_sfx("construir")
        # Encolar: ir a la celda especifica de la matriz
        import threading
        from config import ACTION_DELAY
        if self._stop_event.is_set():
            from penguin import ScriptStopped
            raise ScriptStopped()
        with self._action_lock:
            start = self._queue_end_pos()
            path  = self.world.pathfind(start[0], start[1], wr, wc)
            done  = threading.Event()
            self._action_queue.append({
                "path": path, "action": _do,
                "done": done, "dest": (wr, wc), "delay": ACTION_DELAY,
            })
        while not done.wait(timeout=0.05):
            if self._stop_event.is_set():
                from penguin import ScriptStopped
                raise ScriptStopped()
    def cmd_crear_pinguino(self):
        def _do():
            self._wants_new = True
            self.interp.log("Nuevo pinguino cyborg creado!")
            if hasattr(self, "sound") and self.sound:
                self.sound.play_sfx("crear_pinguino")
        self._enqueue_and_wait("nido", _do)

    # ── Render ──────────────────────────────────────────
    def draw(self, surface, cam_col, cam_row, font,
             tile_size=None, vw=None, vh=None):
        ts  = tile_size or T
        _vw = vw or VW
        _vh = vh or VH

        vc = self.col - cam_col
        vr = self.row - cam_row
        if not (0 <= vc < _vw and 0 <= vr < _vh):
            return

        cx = vc * ts + ts // 2
        cy = vr * ts + HUD_H + ts // 2

        sprite, sprite_walk, sel_ring = self._get_sprites(ts)

        # Path de movimiento (puntos)
        with self._action_lock:
            qs = list(self._action_queue)
        if qs:
            pts = [(self.col, self.row)] + [(c, r) for r, c in qs[0]["path"][:6]]
            for i in range(len(pts) - 1):
                ax = (pts[i][0]   - cam_col) * ts + ts // 2
                ay = (pts[i][1]   - cam_row) * ts + HUD_H + ts // 2
                bx = (pts[i+1][0] - cam_col) * ts + ts // 2
                by = (pts[i+1][1] - cam_row) * ts + HUD_H + ts // 2
                dim = tuple(max(0, c - 100) for c in self.color)
                pygame.draw.line(surface, dim, (ax, ay), (bx, by), 2)

        # Anillo de selección
        if self.selected:
            surface.blit(sel_ring, (vc * ts, vr * ts + HUD_H))

        # Sprite del pingüino centrado en el tile
        sp = sprite_walk if (self._anim_frame == 1 and qs) else sprite
        sw, sh = sp.get_size()
        sx = cx - sw // 2
        sy = cy - sh // 2 - 2
        # Sombra
        shadow = pygame.Surface((sw, 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), (2, 0, sw-4, 4))
        surface.blit(shadow, (sx+2, cy + sh//2 - 2))
        surface.blit(sp, (sx, sy))

        # Indicador "ocupado" (punto naranja)
        if qs:
            pygame.draw.circle(surface, CUI_ORANGE, (cx + ts//2 - 6, cy - ts//2 + 4), 4)
            pygame.draw.circle(surface, (255, 220, 0), (cx + ts//2 - 6, cy - ts//2 + 4), 2)

        # Mini-barras de inventario personal (solo si el tile es suficientemente grande)
        if ts >= 48:
            colors_map = [
                ("Pez",    (80, 160, 255)),
                ("Madera", (160, 100, 40)),
                ("Hielo",  (180, 230, 255)),
            ]
            bar_total_w = ts - 4
            slot_w = bar_total_w // 3
            bar_y  = vr * ts + HUD_H + ts - 8
            bar_x0 = vc * ts + 2
            for i, (res, col_c) in enumerate(colors_map):
                qty = self.personal_inv[res]
                bx0 = bar_x0 + i * slot_w
                pygame.draw.rect(surface, (20, 20, 32), (bx0, bar_y, slot_w - 1, 5))
                fw = int((qty / PERSONAL_MAX) * (slot_w - 1))
                if fw > 0:
                    pygame.draw.rect(surface, col_c, (bx0, bar_y, fw, 5))
                    bright = tuple(min(255, c+60) for c in col_c)
                    pygame.draw.rect(surface, bright, (bx0, bar_y, fw, 1))

        # Nombre (solo si hay espacio)
        if ts >= 48:
            bar_y = vr * ts + HUD_H + ts - 8
            lbl = font.render(self.nombre, True, CUI_WHITE)
            surface.blit(lbl, lbl.get_rect(centerx=cx, top=bar_y + 7))
