# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — penguin.py
#
#  Sistema de threading para bucles infinitos:
#  - El script del jugador corre en un hilo separado.
#  - Cada cmd_*() encola la accion Y bloquea el hilo
#    del script hasta que la animacion termina.
#  - tick() (llamado por el game loop) avanza la animacion
#    y libera el bloqueo cuando llega al destino.
#  - Asi, while True: pescar() funciona perfectamente:
#    cada iteracion espera la anterior.
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import threading
import pygame

from config import PENGUIN_COLORS, MOVE_DELAY, ACTION_DELAY, T, HUD_H, VW, VH, CUI_BLACK, CUI_WHITE, CUI_ORANGE
from world import World, get_zone
from inventory import Inventory


# ─── Excepcion especial para detener el script ──────────
class ScriptStopped(Exception):
    """Lanzada cuando el jugador pulsa Stop mientras el script corre."""
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
        }

    def run(self, code: str) -> list[tuple[str, str]]:
        """
        Ejecuta el codigo en un hilo separado.
        No bloquea el game loop.
        """
        self.out.clear()
        p = self.penguin
        p._stop_event.set()          # detener script anterior si habia
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

        p._script_thread = threading.Thread(
            target=_thread_body, daemon=True)
        p._script_thread.start()
        return []   # output llega asincrono via log()


# ═══════════════════════════════════════════════════════
#  PINGUINO
# ═══════════════════════════════════════════════════════
_counter_lock = threading.Lock()

class Penguin:
    _global_counter = 0

    def __init__(self,
                 nombre: str | None = None,
                 row: int = 3,
                 col: int = 1,
                 world: World | None = None,
                 inventory: Inventory | None = None):
        with _counter_lock:
            Penguin._global_counter += 1
            idx = Penguin._global_counter
        self.nombre    = nombre or f"Pingu-{idx:02d}"
        self.row       = row
        self.col       = col
        self.world     = world
        self.inventory = inventory
        self.interp    = CommandInterpreter(self)
        self.win       = None          # SimulatedPythonWindow | None
        self.selected  = False
        self._wants_new = False
        self.color     = PENGUIN_COLORS[(idx - 1) % len(PENGUIN_COLORS)]

        # ── Threading ────────────────────────────────
        self._stop_event:    threading.Event  = threading.Event()
        self._script_thread: threading.Thread | None = None

        # ── Cola de animacion ─────────────────────────
        # Cada entry: {
        #   "path":   [(r,c), ...],   pasos restantes
        #   "action": callable,       se ejecuta al llegar
        #   "done":   threading.Event  libera el hilo del script
        #   "dest":   (r,c)           destino (para encadenamiento)
        #   "delay":  int             ticks extra al llegar (animacion)
        # }
        self._action_queue: list[dict] = []
        self._move_timer:   int = 0
        self._action_lock   = threading.Lock()

    # ── Tick (llamado por Game.update en el game loop) ──
    def tick(self):
        with self._action_lock:
            if not self._action_queue:
                return
            self._move_timer += 1
            if self._move_timer < MOVE_DELAY:
                return
            self._move_timer = 0

            entry = self._action_queue[0]

            # 1) Aun hay pasos de camino → mover un paso
            if entry["path"]:
                self.row, self.col = entry["path"].pop(0)
                return

            # 2) Llegamos, esperar delay de accion
            if entry.get("delay", 0) > 0:
                entry["delay"] -= 1
                return

            # 3) Ejecutar accion
            action = entry.get("action")
            if action:
                try:
                    action()
                except Exception as e:
                    self.interp.out.append(
                        (f"ERROR en accion: {e}", "err"))
                    if self.win and self.win.active:
                        self.win.out = list(self.interp.out)

            # 4) Liberar el hilo del script
            done = entry.get("done")
            if done:
                done.set()

            self._action_queue.pop(0)

    def stop_script(self):
        """Detiene el script en curso (boton Stop)."""
        self._stop_event.set()
        # Liberar todos los eventos bloqueados para que el hilo pueda terminar
        with self._action_lock:
            for entry in self._action_queue:
                d = entry.get("done")
                if d: d.set()
            self._action_queue.clear()

    # ── Helper interno: encolar con bloqueo ─────────────
    def _enqueue_and_wait(self, target_tipo: str,
                           action: "callable | None"):
        """
        1. Busca el tile mas cercano del tipo pedido.
        2. Calcula el camino BFS.
        3. Encola la entrada.
        4. Bloquea el hilo del script hasta que tick() complete la accion.
        Si se llama stop(), lanza ScriptStopped en el hilo del script.
        """
        # Verificar stop antes de empezar
        if self._stop_event.is_set():
            raise ScriptStopped()

        t = self.world.find_nearest(
            *self._queue_end_pos(), target_tipo)
        if t is None:
            self.interp.log(f"No hay '{target_tipo}' en el mapa.")
            return

        with self._action_lock:
            start = self._queue_end_pos()
            path  = self.world.pathfind(start[0], start[1], t[0], t[1])
            done  = threading.Event()
            self._action_queue.append({
                "path":   path,
                "action": action,
                "done":   done,
                "dest":   t,
                "delay":  ACTION_DELAY,
            })

        # Bloquear el hilo del script hasta que llegue al destino
        while not done.wait(timeout=0.05):
            if self._stop_event.is_set():
                raise ScriptStopped()

    def _queue_end_pos(self) -> tuple[int, int]:
        """Posicion desde la cual calcular el proximo camino."""
        if self._action_queue:
            last_dest = self._action_queue[-1].get("dest")
            if last_dest:
                return last_dest
        return (self.row, self.col)

    # ── Comandos disponibles en el editor ───────────────
    def cmd_pescar(self):
        def _do():
            self.inventory.agregar("Pez")
            self.interp.log(f"Pescado 1 pez! (Total: {self.inventory.obtener('Pez')})")
        self._enqueue_and_wait("costa", _do)

    def cmd_talar(self):
        t = self.world.find_nearest(*self._queue_end_pos(), "arbol")
        if t is None:
            self.interp.log("No hay arboles en el mapa."); return
        def _do():
            pos = (self.row, self.col)
            if self.world.get_tile(*pos).tipo == "arbol":
                self.world.set_tile(*pos, get_zone(*pos))
            self.inventory.agregar("Madera")
            self.interp.log(f"Arbol talado! (Total: {self.inventory.obtener('Madera')})")
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
        def _do():
            self.inventory.agregar("Hielo")
            self.interp.log(f"Hielo extraido! (Total: {self.inventory.obtener('Hielo')})")
        self._enqueue_and_wait("mina", _do)

    def cmd_almacenar(self, material: str):
        def _do():
            n = self.inventory.obtener(material)
            if n > 0:
                self.inventory.rs[material].consumir()
                self.interp.log(f"Almacenado: {material} (quedan {n-1})")
            else:
                self.interp.log(f"No tienes {material}.")
        self._enqueue_and_wait("almacen", _do)

    def cmd_crear_pinguino(self):
        def _do():
            self._wants_new = True
            self.interp.log("Nuevo pinguino cyborg creado!")
        self._enqueue_and_wait("fabrica", _do)

    # ── Render ──────────────────────────────────────────
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

        # Path preview (primeros pasos visibles)
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

        # Sombra + cuerpo
        pygame.draw.circle(surface, CUI_BLACK, (cx + 2, cy + 2), rad)
        pygame.draw.circle(surface, self.color, (cx, cy), rad)
        border = (255, 255, 50) if self.selected else CUI_BLACK
        pygame.draw.circle(surface, border, (cx, cy), rad, 2)

        # Indicador ocupado (punto naranja)
        if queue_snapshot:
            pygame.draw.circle(surface, CUI_ORANGE,
                               (cx + rad - 3, cy - rad + 3), 5)

        # Nombre
        lbl = font.render(self.nombre, True, CUI_WHITE)
        surface.blit(lbl, lbl.get_rect(centerx=cx, top=cy + rad + 2))
