# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — sound.py
#  Gestión de música de fondo y efectos de sonido
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import os
import pygame

SOUNDS_DIR = os.path.join("assets", "sounds")

# Rutas de la música de fondo
_MUSIC = {
    "menu": os.path.join(SOUNDS_DIR, "menu_principal1.mp3"),
    "game": os.path.join(SOUNDS_DIR, "game.mp3"),
}

# Nombres de los efectos de sonido
_SFX_NAMES = ["pescar", "talar", "picar", "construir", "crear_pinguino"]


class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self._ok = True
        except Exception as e:
            print(f"[SONIDO] No se pudo inicializar el mixer: {e}")
            self._ok = False

        self._current_music: str | None = None
        self._sfx: dict[str, pygame.mixer.Sound] = {}

        if self._ok:
            self._load_sfx()

    def _load_sfx(self):
        for name in _SFX_NAMES:
            path = os.path.join(SOUNDS_DIR, f"{name}.mp3")
            if os.path.exists(path):
                try:
                    self._sfx[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"[SONIDO] No se pudo cargar {name}.mp3: {e}")

    # ── Música de fondo ────────────────────────────────
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 800):
        """Cambia la música de fondo con fade. No hace nada si ya está sonando."""
        if not self._ok:
            return
        if self._current_music == name:
            return
        path = _MUSIC.get(name)
        if not path or not os.path.exists(path):
            return
        try:
            pygame.mixer.music.fadeout(fade_ms // 2)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self._current_music = name
        except Exception as e:
            print(f"[SONIDO] Error reproduciendo música '{name}': {e}")

    def stop_music(self, fade_ms: int = 500):
        if not self._ok:
            return
        pygame.mixer.music.fadeout(fade_ms)
        self._current_music = None

    # ── Efectos de sonido ──────────────────────────────
    def play_sfx(self, name: str):
        """Reproduce un efecto de sonido. Seguro para llamar desde hilos."""
        if not self._ok:
            return
        sfx = self._sfx.get(name)
        if sfx:
            try:
                sfx.play()
            except Exception:
                pass
