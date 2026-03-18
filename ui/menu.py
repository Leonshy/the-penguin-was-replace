# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — ui/menu.py
#  Menú principal del juego
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import pygame
from config import WIN_W, WIN_H, CUI_CYAN, CUI_WHITE, CUI_BG


# Opciones del menú: (etiqueta, acción, bloqueado)
_ITEMS_NEW  = [
    ("EMPEZAR",       "start",    False),
    ("CARGAR",        "load",     False),
    ("GUARDAR",       "save",     False),
    ("MODO CREATIVO", "creative", True),
    ("SALIR",         "exit",     False),
]
_ITEMS_GAME = [
    ("CONTINUAR",     "continue", False),
    ("GUARDAR",       "save",     False),
    ("CARGAR",        "load",     False),
    ("MODO CREATIVO", "creative", True),
    ("SALIR",         "exit",     False),
]


class MainMenu:
    def __init__(self):
        self._sel        = 0
        self._message    = ""
        self._msg_timer  = 0
        self._msg_ok     = True   # True=ámbar / False=rojo
        self._timer      = 0
        self._fonts_ok   = False
        self._item_rects: list[pygame.Rect] = []
        self.game_active = False  # True cuando hay partida en curso

    # ── Helpers ────────────────────────────────────────
    def _items(self):
        return _ITEMS_GAME if self.game_active else _ITEMS_NEW

    def _skip_locked(self, direction: int):
        items = self._items()
        for _ in range(len(items)):
            self._sel = (self._sel + direction) % len(items)
            if not items[self._sel][2]:
                break

    def set_message(self, msg: str, ok: bool = True):
        self._message   = msg
        self._msg_timer = pygame.time.get_ticks() + 3000
        self._msg_ok    = ok

    def reset_sel(self):
        self._sel = 0

    # ── Fonts ───────────────────────────────────────────
    def _init_fonts(self):
        if self._fonts_ok:
            return
        self._font_title = pygame.font.SysFont("Courier New", 30, bold=True)
        self._font_sub   = pygame.font.SysFont("Courier New", 13)
        self._font_item  = pygame.font.SysFont("Courier New", 21, bold=True)
        self._font_msg   = pygame.font.SysFont("Courier New", 13)
        self._fonts_ok   = True

    # ── Eventos ────────────────────────────────────────
    def handle_event(self, event) -> str | None:
        """Devuelve la acción elegida o None."""
        items = self._items()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._skip_locked(-1)
            elif event.key == pygame.K_DOWN:
                self._skip_locked(+1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._activate()

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mx, my) and not items[i][2]:
                    self._sel = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._item_rects):
                if rect.collidepoint(mx, my):
                    if items[i][2]:
                        self.set_message("Modo Creativo: Proximamente...", ok=False)
                        return None
                    self._sel = i
                    return self._activate()

        return None

    def _activate(self) -> str | None:
        items  = self._items()
        action = items[self._sel][1]
        if items[self._sel][2]:
            self.set_message("Modo Creativo: Proximamente...", ok=False)
            return None
        return action

    # ── Render ─────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        self._init_fonts()
        self._timer += 1
        items = self._items()
        self._item_rects = []

        # Fondo
        surface.fill((4, 4, 10))
        for y in range(0, WIN_H, 3):
            pygame.draw.line(surface, (0, 0, 0), (0, y), (WIN_W, y))

        # Título
        shadow = self._font_title.render("THE PENGUIN WAS REPLACE", True, (0, 55, 55))
        title  = self._font_title.render("THE PENGUIN WAS REPLACE", True, CUI_CYAN)
        tx = WIN_W // 2 - title.get_width() // 2
        surface.blit(shadow, (tx + 2, 94))
        surface.blit(title,  (tx, 92))

        sub = self._font_sub.render("hackathon edition  —  v0.1", True, (45, 90, 90))
        surface.blit(sub, (WIN_W // 2 - sub.get_width() // 2, 130))

        pygame.draw.line(surface, (0, 70, 70),
                         (WIN_W // 2 - 170, 150), (WIN_W // 2 + 170, 150))

        # Ítems
        ITEM_H = 50
        item_y = 170
        for i, (label, action, locked) in enumerate(items):
            rect = pygame.Rect(WIN_W // 2 - 170, item_y - 2, 340, ITEM_H - 6)
            self._item_rects.append(rect)

            is_sel = (i == self._sel)

            if locked:
                color = (38, 42, 58)
                text  = f"  {label}  (proximamente)"
            elif is_sel:
                color = (255, 200, 60)
                bg    = pygame.Surface((rect.w, rect.h))
                bg.fill((28, 22, 4))
                bg.set_alpha(210)
                surface.blit(bg, rect.topleft)
                pygame.draw.rect(surface, (90, 55, 0), rect, 1)
                text = f"[ {label} ]"
            else:
                color = CUI_WHITE
                text  = f"[ {label} ]"

            s = self._font_item.render(text, True, color)
            surface.blit(s, (WIN_W // 2 - s.get_width() // 2, item_y + 6))

            if is_sel and not locked and (self._timer // 18) % 2 == 0:
                arrow = self._font_item.render("▶", True, (255, 150, 0))
                surface.blit(arrow, (WIN_W // 2 - 155, item_y + 6))

            item_y += ITEM_H

        # Mensaje de feedback
        if self._message and pygame.time.get_ticks() < self._msg_timer:
            col   = (255, 160, 0) if self._msg_ok else (220, 80, 80)
            msg_s = self._font_msg.render(self._message, True, col)
            my    = item_y + 14
            surface.blit(msg_s, (WIN_W // 2 - msg_s.get_width() // 2, my))
        else:
            self._message = ""

        # Pingüino decorativo
        for i, line in enumerate(["  (._.) ", " (> 🐟 <)", "  (/ \\) "]):
            ps = self._font_sub.render(line, True, (35, 75, 75))
            surface.blit(ps, (WIN_W - 115, WIN_H - 95 + i * 17))

        # Hint
        hint = self._font_msg.render(
            "↑↓ navegar   ENTER seleccionar   clic con mouse",
            True, (30, 40, 60))
        surface.blit(hint, (WIN_W // 2 - hint.get_width() // 2, WIN_H - 26))
