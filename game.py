# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — game.py
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import traceback
import pygame

from config import (
    WIN_W, WIN_H, HUD_H, BAR_H,
    VW, VH, WW, WH, T, FPS,
    CUI_BG, CUI_CYAN, CUI_GREEN, CUI_ORANGE, CUI_GRAY, CUI_WHITE,
    COMP_POSITIONS,
)
from world import World
from inventory import Inventory
from penguin import Penguin
from ui.window import SimulatedPythonWindow
from ui.terminal import ComputerTerminal

# Velocidad de scroll de camara con flechas (frames entre pasos)
CAM_SPEED = 5


class Game:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Cyborg Penguins")
        self.clock   = pygame.time.Clock()
        self.running = True

        self.font_sm  = pygame.font.SysFont("Courier New", 12)
        self.font_md  = pygame.font.SysFont("Courier New", 15)
        self.font_big = pygame.font.SysFont("Courier New", 19, bold=True)

        self.inventory = Inventory()
        self.world     = World()
        self.computers = [ComputerTerminal(r, c) for r, c in COMP_POSITIONS]

        self.penguins:    list[Penguin]                = []
        self.active_win:  SimulatedPythonWindow | None = None
        self.active_comp: ComputerTerminal | None      = None

        # Camara
        self.cam_col     = 0
        self.cam_row     = 0
        self._cam_timer  = 0   # para limitar velocidad de scroll

        self._spawn(7, 9, "Pingu-01")
        self._center_camera()

    # ── Helpers ─────────────────────────────────────
    def _spawn(self, row: int, col: int,
               nombre: str | None = None) -> Penguin:
        p = Penguin(nombre=nombre, row=row, col=col,
                    world=self.world, inventory=self.inventory)
        self.penguins.append(p)
        return p

    def _center_camera(self):
        """Centra la camara en el pinguino seleccionado."""
        target = next((p for p in self.penguins if p.selected),
                      self.penguins[0] if self.penguins else None)
        if target:
            self.cam_col = max(0, min(target.col - VW // 2, WW - VW))
            self.cam_row = max(0, min(target.row - VH // 2, WH - VH))

    # ── Eventos ─────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit(); return

            # La ventana del editor consume eventos de teclado
            if self.active_win and self.active_win.active:
                consumed = self.active_win.handle_event(event)
                if not self.active_win.active:
                    self.active_win = None
                if consumed:
                    continue

            if self.active_comp and self.active_comp.show:
                self.active_comp.handle_event(event)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(event.pos)

    def _on_click(self, pos):
        mx, my = pos
        if my < HUD_H or my >= HUD_H + VH * T:
            return
        wc = self.cam_col + mx // T
        wr = self.cam_row + (my - HUD_H) // T
        if not (0 <= wr < WH and 0 <= wc < WW):
            return

        for p in self.penguins:
            if p.row == wr and p.col == wc:
                for pp in self.penguins:
                    pp.selected = False
                p.selected = True
                self._center_camera()
                if p.win:
                    p.win.active = True
                    self.active_win = p.win
                else:
                    p.win = SimulatedPythonWindow(p)
                    self.active_win = p.win
                return

        for comp in self.computers:
            if comp.row == wr and comp.col == wc:
                self.active_comp = comp
                comp.show = True
                return

    # ── Update ──────────────────────────────────────
    def update(self):
        if self.active_win and not self.active_win.active:
            self.active_win = None

        # Regrowth de arboles
        self.world.update(pygame.time.get_ticks())

        for p in self.penguins:
            p.tick()
            if p._wants_new:
                p._wants_new = False
                # Fabrica: r0-5, c14-20
                if p.row <= 5 and p.col >= 14:
                    nuevo = self._spawn(7, 9)
                    print(f"[Fabrica] Creado: {nuevo.nombre}")

        # ── Scroll de camara con teclas de flecha ────
        # Solo cuando el editor NO esta activo (para no interferir con texto)
        editor_open = self.active_win and self.active_win.active
        if not editor_open:
            self._cam_timer += 1
            if self._cam_timer >= CAM_SPEED:
                self._cam_timer = 0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.cam_col = max(0, self.cam_col - 1)
                if keys[pygame.K_RIGHT]:
                    self.cam_col = min(WW - VW, self.cam_col + 1)
                if keys[pygame.K_UP]:
                    self.cam_row = max(0, self.cam_row - 1)
                if keys[pygame.K_DOWN]:
                    self.cam_row = min(WH - VH, self.cam_row + 1)

    # ── Draw ─────────────────────────────────────────
    def draw(self):
        self.screen.fill(CUI_BG)
        self.world.draw(self.screen, self.cam_col, self.cam_row, self.font_sm)
        for p in self.penguins:
            p.draw(self.screen, self.cam_col, self.cam_row, self.font_sm)
        for comp in self.computers:
            comp.draw(self.screen, self.font_sm)
        self._draw_hud()
        if self.active_win and self.active_win.active:
            self.active_win.draw(self.screen)
        pygame.display.flip()

    def _draw_hud(self):
        pygame.draw.rect(self.screen, (11, 11, 25), (0, 0, WIN_W, HUD_H))
        pygame.draw.line(self.screen, CUI_CYAN, (0, HUD_H - 1), (WIN_W, HUD_H - 1))

        self.screen.blit(
            self.font_big.render("CYBORG PENGUINS", True, CUI_CYAN),
            (10, 4))

        # Inventario GLOBAL de la colonia
        self.screen.blit(
            self.font_md.render(self.inventory.hud(), True, CUI_GREEN),
            self.font_md.render(self.inventory.hud(), True, CUI_GREEN)
                .get_rect(right=WIN_W - 8, top=4))

        sel = next((p for p in self.penguins if p.selected), None)
        if sel:
            zone   = self.world.zone_name(sel.row, sel.col)
            status = " [RUNNING]" if (sel.win and sel.win.running) else ""
            self.screen.blit(
                self.font_md.render(
                    f"[ {zone} ]  {sel.nombre}{status}",
                    True, CUI_ORANGE),
                (10, 26))

            # Inventario PERSONAL del pinguino seleccionado
            inv_str = sel.inv_status()
            inv_s   = self.font_sm.render(
                f"Mochila:  {inv_str}", True, (180, 200, 255))
            self.screen.blit(inv_s, (10, 46))

        # Indicadores de camara / zonas
        zone_labels = [
            ("Almacen r0-5,c7-13",  0, 5,  7, 13),
            ("Fabrica r0-5,c14-20", 0, 5, 14, 20),
            ("Mina    r6-11,c0-6",  6, 11, 0,  6),
            ("Pesca   r6-11,c7-13", 6, 11, 7, 13),
            ("Bosque  r6-11,c14+",  6, 11, 14, 20),
            ("Mar     r12-13",      12, 13, 0, 20),
        ]
        x_off = WIN_W - 200
        for i, (name, r0, r1, c0, c1) in enumerate(zone_labels):
            vis = (self.cam_row <= r1 and self.cam_row + VH > r0
                   and self.cam_col <= c1 and self.cam_col + VW > c0)
            col = CUI_CYAN if vis else CUI_GRAY
            short = name.split()[0]
            s = self.font_sm.render(short, True, col)
            self.screen.blit(s, (x_off + (i % 3) * 66, 4 + (i // 3) * 14))

        # Barra inferior
        bar_y = HUD_H + VH * T
        pygame.draw.rect(self.screen, (8, 8, 18), (0, bar_y, WIN_W, BAR_H))
        pygame.draw.line(self.screen, CUI_GRAY, (0, bar_y), (WIN_W, bar_y))
        self.screen.blit(
            self.font_sm.render(
                "Clic pinguino → editor  |  F5 run  |  F6 stop  |  "
                "Flechas → mover camara  |  Inv personal max 5",
                True, (55, 60, 88)),
            (4, bar_y + 3))

    # ── Loop ─────────────────────────────────────────
    def run(self):
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception:
                print("=" * 60)
                traceback.print_exc()
                print("=" * 60)
                try:
                    font = pygame.font.SysFont("Courier New", 13)
                    s = font.render("Error interno (ver consola)", True, (220, 60, 60))
                    self.screen.blit(s, (8, WIN_H - 36))
                    pygame.display.flip()
                except Exception:
                    pass
            self.clock.tick(FPS)
        self._quit()

    def _quit(self):
        for p in self.penguins:
            p.stop_script()
        pygame.quit()
        import sys; sys.exit()