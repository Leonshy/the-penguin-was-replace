# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — penguin.py
#
#  Sistema de threading para bucles infinitos.
#  Inventario personal: max 5 por recurso.
#  Al llegar a 5, el pingüino debe ir a almacenar.
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import threading
import pygame

from config import (
    PENGUIN_COLORS, MOVE_DELAY, ACTION_DELAY,
    T, HUD_H, VW, VH, CUI_BLACK, CUI_WHITE, CUI_ORANGE, CUI_RED,
)
from world import World, get_zone
from inventory import Inventory

PERSONAL_MAX = 5   # maximo de cada recurso en el inventario personal


class ScriptStopped(Exception):
    """Lanzada cuando el jugador pulsa Stop."""
    pass


# ═══════════════════════════════════════════════════════
#  INTERPRETE DE COMANDOS
# ═══════════════════════════════════════════════════════
class CommandInterpreter:
    def __init__(self, penguin: "Penguin"):
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
        safe_builtins = {
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
            "__builtins__": safe_builtins,
            "pescar":         p.cmd_pescar,
            "talar":          p.cmd_talar,
            "picar_hielo":    p.cmd_picar_hielo,
            "almacenar":      p.cmd_almacenar,
            "crear_pinguino": p.cmd_crear_pinguino,
            # Utilidades de consulta
            "inventario_lleno": p.inventario_lleno,
            "inventario":       p.personal_inv,
        }

    def run(self, code: str) -> list[tuple[str, str]]:
        self.out.clear()
        p = self.penguin
        p._stop_event.set()
        if p._script_thread and p._script_thread.is_alive():
            p._script_thread.join(timeout=0.5)
        p._stop_event.clear()
        p._action_queue.clear()

        def _thread_body():
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

        p._script_thread = threading.Thread(target=_thread_body, daemon=True)
        p._script_thread.start()
        return []


# ═══════════════════════════════════════════════════════
#  PINGUINO
# ═══════════════════════════════════════════════════════
_counter_lock = threading.Lock()


class Penguin:
    _global_counter = 0

    def __init__(self,
                 nombre: str | None = None,
                 row: int = 7,
                 col: int = 9,
                 world: World | None = None,
                 inventory: Inventory | None = None):
        with _counter_lock:
            Penguin._global_counter += 1
            idx = Penguin._global_counter
        self.nombre    = nombre or f"Pingu-{idx:02d}"
        self.row       = row
        self.col       = col
        self.world     = world
        self.inventory = inventory   # inventario global de la colonia
        self.interp    = CommandInterpreter(self)
        self.win       = None
        self.selected  = False
        self._wants_new = False
        self.color     = PENGUIN_COLORS[(idx - 1) % len(PENGUIN_COLORS)]

        # ── Inventario personal (max 5 por recurso) ──
        self.personal_inv: dict[str, int] = {
            "Pez": 0, "Madera": 0, "Hielo": 0
        }

        # ── Threading ────────────────────────────────
        self._stop_event:    threading.Event        = threading.Event()
        self._script_thread: threading.Thread | None = None
        self._action_queue:  list[dict]             = []
        self._move_timer:    int                    = 0
        self._action_lock    = threading.Lock()

    # ── Consultas de inventario ──────────────────────
    def inventario_lleno(self, material: str) -> bool:
        """Devuelve True si el inventario personal esta lleno para ese material."""
        return self.personal_inv.get(material, 0) >= PERSONAL_MAX

    def _inv_total(self) -> int:
        return sum(self.personal_inv.values())

    def inv_status(self) -> str:
        return "  ".join(
            f"{k}:{v}/{PERSONAL_MAX}" for k, v in self.personal_inv.items()
        )

    # ── Tick ────────────────────────────────────────
    def tick(self):
        with self._action_lock:
            if not self._action_queue:
                return
            self._move_timer += 1
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
                    self.interp.out.append((f"ERROR en accion: {e}", "err"))
                    if self.win and self.win.active:
                        self.win.out = list(self.interp.out)

            done = entry.get("done")
            if done:
                done.set()

            self._action_queue.pop(0)

    def stop_script(self):
        self._stop_event.set()
        with self._action_lock:
            for entry in self._action_queue:
                d = entry.get("done")
                if d:
                    d.set()
            self._action_queue.clear()

    # ── Helper de cola ───────────────────────────────
    def _enqueue_and_wait(self, target_tipo: str, action):
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

    def _queue_end_pos(self) -> tuple[int, int]:
        if self._action_queue:
            last_dest = self._action_queue[-1].get("dest")
            if last_dest:
                return last_dest
        return (self.row, self.col)

    # ── Comandos ────────────────────────────────────
    def cmd_pescar(self):
        if self.personal_inv["Pez"] >= PERSONAL_MAX:
            self.interp.log(
                f"Inventario de Pez lleno ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                "Usá almacenar('Pez') primero.")
            return
        def _do():
            self.personal_inv["Pez"] += 1
            n = self.personal_inv["Pez"]
            self.interp.log(
                f"Pescado! Pez: {n}/{PERSONAL_MAX}"
                + (" — LLENO!" if n >= PERSONAL_MAX else ""))
        self._enqueue_and_wait("costa", _do)

    def cmd_talar(self):
        if self.personal_inv["Madera"] >= PERSONAL_MAX:
            self.interp.log(
                f"Inventario de Madera lleno ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                "Usá almacenar('Madera') primero.")
            return
        t = self.world.find_nearest(*self._queue_end_pos(), "arbol")
        if t is None:
            self.interp.log("No hay arboles disponibles."); return
        def _do():
            pos = (self.row, self.col)
            if self.world.get_tile(*pos).tipo == "arbol":
                self.world.cut_tree(pos[0], pos[1], pygame.time.get_ticks())
            self.personal_inv["Madera"] += 1
            n = self.personal_inv["Madera"]
            self.interp.log(
                f"Arbol talado! Regrowth en 20s. Madera: {n}/{PERSONAL_MAX}"
                + (" — LLENO!" if n >= PERSONAL_MAX else ""))
        with self._action_lock:
            start = self._queue_end_pos()
            path  = self.world.pathfind(start[0], start[1], t[0], t[1])
            done  = threading.Event()
            self._action_queue.append({
                "path": path, "action": _do,
                "done": done, "dest": t, "delay": ACTION_DELAY,
            })
        while not done.wait(timeout=0.05):
            if self._stop_event.is_set():
                raise ScriptStopped()

    def cmd_picar_hielo(self):
        if self.personal_inv["Hielo"] >= PERSONAL_MAX:
            self.interp.log(
                f"Inventario de Hielo lleno ({PERSONAL_MAX}/{PERSONAL_MAX})! "
                "Usá almacenar('Hielo') primero.")
            return
        def _do():
            self.personal_inv["Hielo"] += 1
            n = self.personal_inv["Hielo"]
            self.interp.log(
                f"Hielo extraido! Hielo: {n}/{PERSONAL_MAX}"
                + (" — LLENO!" if n >= PERSONAL_MAX else ""))
        self._enqueue_and_wait("mina", _do)

    def cmd_almacenar(self, material: str):
        """
        Lleva al pinguino al almacen y deposita
        TODOS los recursos del material dado.
        """
        if material not in self.personal_inv:
            self.interp.log(f"Material desconocido: '{material}'. Usa 'Pez', 'Madera' o 'Hielo'.")
            return
        if self.personal_inv[material] == 0:
            self.interp.log(f"No tienes {material} para almacenar.")
            return
        def _do():
            qty = self.personal_inv[material]
            self.inventory.agregar(material, qty)
            self.personal_inv[material] = 0
            total = self.inventory.obtener(material)
            self.interp.log(
                f"Almacenado {qty} {material}. "
                f"Colonia total: {total}")
        self._enqueue_and_wait("almacen", _do)

    def cmd_crear_pinguino(self):
        def _do():
            self._wants_new = True
            self.interp.log("Nuevo pinguino cyborg creado!")
        self._enqueue_and_wait("fabrica", _do)

    # ── Render ──────────────────────────────────────
    def draw(self, surface: pygame.Surface,
             cam_col: int, cam_row: int,
             font: pygame.font.Font):
        vc = self.col - cam_col
        vr = self.row - cam_row
        if not (0 <= vc < VW and 0 <= vr < VH):
            return
        cx  = vc * T + T // 2
        cy  = vr * T + HUD_H + T // 2
        rad = T // 3

        # Path preview
        with self._action_lock:
            queue_snapshot = list(self._action_queue)
        if queue_snapshot:
            path = queue_snapshot[0]["path"]
            pts  = [(self.col, self.row)] + [(c, r) for r, c in path[:8]]
            if len(pts) > 1:
                for i in range(len(pts) - 1):
                    ax = (pts[i][0]   - cam_col) * T + T // 2
                    ay = (pts[i][1]   - cam_row) * T + HUD_H + T // 2
                    bx = (pts[i+1][0] - cam_col) * T + T // 2
                    by = (pts[i+1][1] - cam_row) * T + HUD_H + T // 2
                    dim = tuple(max(0, c - 90) for c in self.color)
                    pygame.draw.line(surface, dim, (ax, ay), (bx, by), 2)

        # Cuerpo
        pygame.draw.circle(surface, CUI_BLACK, (cx + 2, cy + 2), rad)
        pygame.draw.circle(surface, self.color, (cx, cy), rad)
        border = (255, 255, 50) if self.selected else CUI_BLACK
        pygame.draw.circle(surface, border, (cx, cy), rad, 2)

        if queue_snapshot:
            pygame.draw.circle(surface, CUI_ORANGE,
                               (cx + rad - 3, cy - rad + 3), 5)

        # Barra de inventario personal (mini barras de colores)
        colors_map = {"Pez": (80, 160, 255), "Madera": (160, 100, 40), "Hielo": (180, 230, 255)}
        bar_w_total = rad * 2
        slot_w = bar_w_total // 3
        bar_y  = cy + rad + 2
        for i, (res, col_c) in enumerate(colors_map.items()):
            qty = self.personal_inv[res]
            bx0 = cx - rad + i * slot_w
            # Fondo gris oscuro
            pygame.draw.rect(surface, (40, 40, 55),
                             (bx0, bar_y, slot_w - 1, 5))
            # Relleno proporcional
            fill_w = int((qty / PERSONAL_MAX) * (slot_w - 1))
            if fill_w > 0:
                pygame.draw.rect(surface, col_c,
                                 (bx0, bar_y, fill_w, 5))

        lbl = font.render(self.nombre, True, CUI_WHITE)
        surface.blit(lbl, lbl.get_rect(centerx=cx, top=bar_y + 7))