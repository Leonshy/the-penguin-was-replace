# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — progress.py
#  Rastrea hitos del juego y desbloquea archivos en la
#  terminal de la PC conforme el jugador avanza.
# ═══════════════════════════════════════════════════════
from __future__ import annotations


class ProgressTracker:
    """
    Hitos y archivos que se desbloquean:
      PC reparada         -> tutorial_bash.txt + pescar.vim
      1  pez pescado      -> while_loops.txt
      5  peces pescados   -> almacenar.txt
      100 peces almacen   -> talar.txt
      150 peces+150 madera almacen -> picar_hielo.txt
      200p+200m+100h almacen       -> construir_nido.txt
                                      crear_pinguino.txt
    """

    def __init__(self):
        # Contadores rastreados en tiempo real
        self.fish_caught_total: int = 0   # acumulado, solo peces cogidos

        # Hitos ya logrados (para no repetir notificaciones)
        self._unlocked: set[str] = set()

        # Referencia a la terminal (se asigna en Game.__init__)
        self.terminal   = None
        self.on_unlock  = None   # callback(filename) — se asigna en Game.__init__

    # ── Notificacion de progreso ─────────────────────
    def on_fish_caught(self):
        """Llamar cada vez que un pinguino pesca un pez."""
        self.fish_caught_total += 1
        self._check()

    def on_penguin_created(self, total: int):
        """Llamar cada vez que se crea un pingüino nuevo."""
        if total >= 3:
            self._unlock("transmision_final.txt")

    def on_pc_repaired(self):
        """Llamar cuando el jugador repara la PC."""
        self._unlock("tutorial_bash.txt")
        self._unlock("pescar.vim")

    def check_storage(self, fish: int, wood: int, ice: int):
        """Llamar cada frame con los valores actuales del almacen."""
        if fish >= 35:
            self._unlock("talar.txt")
        if fish >= 70 and wood >= 35:
            self._unlock("picar_hielo.txt")
        if fish >= 100 and wood >= 70 and ice >= 50:
            self._unlock("construir_nido.txt")
            self._unlock("crear_pinguino.txt")

    # ── Privado ──────────────────────────────────────
    def _check(self):
        if self.fish_caught_total >= 1:
            self._unlock("while_loops.txt")
        if self.fish_caught_total >= 5:
            self._unlock("almacenar.txt")

    def _unlock(self, filename: str):
        if filename not in self._unlocked:
            self._unlocked.add(filename)
            if self.terminal:
                self.terminal.unlock_file(filename)
            if self.on_unlock:
                self.on_unlock(filename)
