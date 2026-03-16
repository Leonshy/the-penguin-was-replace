# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — colony.py
#
#  La colonia consume automaticamente 1 pez del almacen
#  cada FISH_CONSUME_SEC segundos.
#
#  - Si hay peces: los consume y sube la barra de hambre.
#  - Si NO hay peces: la barra baja a HUNGER_DRAIN_SEC pts/seg.
#  - Si hunger llega a 0 y hay >1 pinguino: muere 1 cada 10s.
# ═══════════════════════════════════════════════════════
from __future__ import annotations

from config import (
    HUNGER_MAX, HUNGER_DRAIN_SEC, HUNGER_PER_FISH,
    FISH_CONSUME_SEC, HUNGER_DEATH_MS,
)


class Colony:
    def __init__(self, inventory=None):
        self.inventory        = inventory
        self.hunger: float    = HUNGER_MAX
        self.nidos: int       = 0
        self.death_log: list[str] = []

        self._last_death_ms:   float = 0.0
        self._fish_timer_sec: float = 0.0
        self.alive_count: int = 1

    # ── Nidos ───────────────────────────────────────
    def build_nido(self, row: int, col: int):
        self.nidos += 1

    # ── Update (llamado cada frame) ─────────────────
    def update(self, dt_sec: float, current_ms: float,
               penguins: list) -> list:
        """
        Logica de hambre:
          1. Cada FISH_CONSUME_SEC segundos, intenta comer 1 pez del almacen.
             - Si hay pez: lo consume, hunger += HUNGER_PER_FISH
             - Si no hay: hunger -= HUNGER_DRAIN_SEC * dt  (baja continuamente)
          2. Si hunger == 0 y >1 pinguino vivo: mata 1 cada HUNGER_DEATH_MS.
        Devuelve lista de pinguinos que deben morir.
        """
        # Avanzar el temporizador de consumo de peces
        alive_count = max(1, sum(1 for p in penguins if p.alive))
        self.alive_count = alive_count   # para el HUD
        self._fish_timer_sec += dt_sec
        ate_fish = False

        if self._fish_timer_sec >= FISH_CONSUME_SEC:
            self._fish_timer_sec -= FISH_CONSUME_SEC
            # Intentar comer 1 pez del almacen
            if self.inventory and self.inventory.consumir("Pez", 1):
                self.hunger = min(HUNGER_MAX,
                                  self.hunger + HUNGER_PER_FISH)
                ate_fish = True

        # Si no hubo pez en este ciclo, la barra baja — escalada por pinguinos
        # Cada pinguino adicional aumenta el drain: 1 ping=1x, 2=1.5x, 3=2x...
        if not ate_fish:
            fish_en_almacen = (self.inventory.obtener("Pez") > 0
                               if self.inventory else False)
            if not fish_en_almacen:
                drain_mult = 1.0 + (alive_count - 1) * 0.5
                self.hunger = max(0.0,
                                  self.hunger - HUNGER_DRAIN_SEC * drain_mult * dt_sec)

        # Matar pinguinos si la barra llega a 0
        to_kill = []
        if self.hunger <= 0.0:
            alive = [p for p in penguins if p.alive]
            if len(alive) > 1:
                elapsed = current_ms - self._last_death_ms
                if elapsed >= HUNGER_DEATH_MS:
                    self._last_death_ms = current_ms
                    victim = alive[-1]
                    to_kill.append(victim)
                    self.death_log.append(
                        f"{victim.nombre} murio de hambre!")

        return to_kill

    # ── HUD ─────────────────────────────────────────
    @property
    def hunger_pct(self) -> float:
        return self.hunger / HUNGER_MAX

    def hunger_color(self) -> tuple[int, int, int]:
        p = self.hunger_pct
        if p > 0.5:
            r = int(255 * (1 - p) * 2)
            return (r, 200, 40)
        else:
            g = int(200 * p * 2)
            return (255, g, 20)

    def next_eat_pct(self) -> float:
        """Porcentaje del temporizador hasta el proximo pez consumido."""
        return self._fish_timer_sec / FISH_CONSUME_SEC