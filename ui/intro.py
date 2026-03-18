# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — ui/intro.py
#  Pantalla de introducción narrativa (4 bloques)
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import pygame
from config import WIN_W, WIN_H, CUI_WHITE, CUI_CYAN

# Cada línea es (texto, estilo)
# estilos: "normal" | "highlight" | "gap" | "small"
BLOCKS: list[list[tuple[str, str]]] = [
    [
        ("", "gap"),
        ("", "gap"),
        ("El ártico murió en silencio.", "normal"),
        ("No hubo explosión. No hubo guerra.", "normal"),
        ("Solo el hielo que se fue, centímetro a centímetro,", "normal"),
        ("hasta que un día no quedó nada.", "normal"),
        ("", "gap"),
        ("Solo quedamos nosotros.", "highlight"),
    ],
    [
        ("", "gap"),
        ("Los científicos lo llamaron Proyecto CYBORG.", "normal"),
        ("Nosotros lo llamamos sobrevivir.", "normal"),
        ("", "gap"),
        ("Tomaron al último pingüino salvaje,", "normal"),
        ("le dieron un ojo que ve en la oscuridad,", "normal"),
        ("un brazo que no siente el frío,", "normal"),
        ('y un nombre: Pingu-01.', "normal"),
        ("", "gap"),
        ("Ese eres tú.", "highlight"),
    ],
    [
        ("", "gap"),
        ("Tu base está en ruinas.", "normal"),
        ("La computadora principal lleva semanas sin señal.", "normal"),
        ("Sin ella, no podés coordinar nada.", "normal"),
        ("Sin coordinación, la colonia no existe.", "normal"),
        ("", "gap"),
        ("Primero lo primero:", "normal"),
        ("encontrá la PC y repárala.", "highlight"),
    ],
    [
        ("", "gap"),
        ("No hay manual. No hay instructor.", "normal"),
        ("Hay una pantalla parpadeando en la oscuridad", "normal"),
        ("y un código que escribir.", "normal"),
        ("", "gap"),
        ("El resto depende de vos.", "normal"),
        ("", "gap"),
        ("La primera computadora está encendida. Acercate.", "highlight"),
    ],
]


class IntroScreen:
    _LINE_H = 34

    def __init__(self):
        self._block    = 0
        self.done      = False
        self._timer    = 0
        self._fonts_ok = False

    def _init_fonts(self):
        if self._fonts_ok:
            return
        self._font_normal = pygame.font.SysFont("Courier New", 18)
        self._font_hl     = pygame.font.SysFont("Courier New", 20, bold=True)
        self._font_ui     = pygame.font.SysFont("Courier New", 14)
        self._fonts_ok    = True

    # ── Input ────────────────────────────────────────────
    def handle_event(self, event) -> bool:
        """Devuelve True cuando la intro termina."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                return True
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._advance()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._advance()
        return False

    def _advance(self) -> bool:
        self._block += 1
        self._timer  = 0
        if self._block >= len(BLOCKS):
            self.done = True
            return True
        return False

    # ── Render ───────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        self._init_fonts()
        self._timer += 1

        # Fondo negro puro — contraste máximo
        surface.fill((4, 4, 10))

        # Scanlines sutiles
        for y in range(0, WIN_H, 3):
            pygame.draw.line(surface, (0, 0, 0), (0, y), (WIN_W, y))

        if self._block >= len(BLOCKS):
            return

        block = BLOCKS[self._block]

        # Calcular altura total del bloque para centrarlo
        total_h = len(block) * self._LINE_H
        start_y = (WIN_H - total_h) // 2 - 30

        for i, (text, style) in enumerate(block):
            if style == "gap" or not text:
                continue
            if style == "highlight":
                color = CUI_CYAN
                font  = self._font_hl
            else:
                color = CUI_WHITE
                font  = self._font_normal

            surf = font.render(text, True, color)
            x = WIN_W // 2 - surf.get_width() // 2
            y = start_y + i * self._LINE_H
            surface.blit(surf, (x, y))

        # Indicador de bloque (arriba derecha)
        ind = self._font_ui.render(
            f"[ {self._block + 1} / {len(BLOCKS)} ]",
            True, (50, 70, 90))
        surface.blit(ind, (WIN_W - ind.get_width() - 20, 20))

        # "[CONTINUAR]" parpadeante (abajo centro)
        if (self._timer // 25) % 2 == 0:
            cont = self._font_hl.render("[ CONTINUAR ]", True, CUI_CYAN)
            surface.blit(cont, (WIN_W // 2 - cont.get_width() // 2, WIN_H - 70))

        # Hint ESC (abajo izquierda)
        esc = self._font_ui.render("ESC — saltar intro", True, (35, 45, 65))
        surface.blit(esc, (20, WIN_H - 26))
