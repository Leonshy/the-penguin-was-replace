# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — game.py
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import traceback
import pygame

from config import (
    WIN_W, WIN_H, HUD_H, BAR_H,
    VW, VH, WW, WH, T, FPS,
    CUI_BG, CUI_CYAN, CUI_GREEN, CUI_ORANGE, CUI_GRAY, CUI_WHITE, CUI_RED,
    COMP_POSITIONS,
    HUNGER_MAX,
)
from world import World
from inventory import Inventory
from penguin import Penguin
from colony import Colony
from ui.window import SimulatedPythonWindow
from ui.terminal import ComputerTerminal

CAM_SPEED = 4   # frames entre pasos de camara


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
        self.colony    = Colony(self.inventory)
        self.computers = [ComputerTerminal(r, c) for r, c in COMP_POSITIONS]

        self.penguins:    list[Penguin]                = []
        self.active_win:  SimulatedPythonWindow | None = None
        self.active_comp: ComputerTerminal | None      = None

        self.cam_col    = 0
        self.cam_row    = 0
        self._cam_timer = 0

        # Mensajes de eventos (muertes, etc.)
        self._event_msgs: list[tuple[str, float, tuple]] = []
        # (texto, tiempo_expira_ms, color)

        self._last_ms  = pygame.time.get_ticks()
        self._spawn(7, 9, "Pingu-01")
        self._center_camera()

    # ── Helpers ─────────────────────────────────────
    def _spawn(self, row: int, col: int,
               nombre: str | None = None) -> Penguin:
        p = Penguin(nombre=nombre, row=row, col=col,
                    world=self.world, inventory=self.inventory,
                    colony=self.colony)
        self.penguins.append(p)
        return p

    def _center_camera(self):
        target = next((p for p in self.penguins if p.selected and p.alive),
                      next((p for p in self.penguins if p.alive), None))
        if target:
            self.cam_col = max(0, min(target.col - VW // 2, WW - VW))
            self.cam_row = max(0, min(target.row - VH // 2, WH - VH))

    def _push_msg(self, text: str,
                  color: tuple = (255, 80, 80), duration_ms: float = 3000):
        expire = pygame.time.get_ticks() + duration_ms
        self._event_msgs.append((text, expire, color))
        if len(self._event_msgs) > 6:
            self._event_msgs.pop(0)

    # ── Eventos ─────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit(); return

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
            if p.alive and p.row == wr and p.col == wc:
                for pp in self.penguins: pp.selected = False
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
        now    = pygame.time.get_ticks()
        dt_sec = (now - self._last_ms) / 1000.0
        self._last_ms = now

        if self.active_win and not self.active_win.active:
            self.active_win = None

        self.world.update(now)

        # ── Hambre ──────────────────────────────────
        victims = self.colony.update(dt_sec, now, self.penguins)
        for p in victims:
            p.alive = False
            p.stop_script()
            if p == next((x for x in self.penguins if x.selected), None):
                # Pasar seleccion al primero vivo
                alive = [x for x in self.penguins if x.alive]
                if alive:
                    alive[0].selected = True
            self._push_msg(
                f"☠ {p.nombre} murio de hambre!",
                color=(255, 60, 60), duration_ms=5000)
            print(f"[Hambre] {p.nombre} muerto.")

        # Limpiar pinguinos muertos de la lista
        for p in self.penguins:
            if not p.alive:
                self.penguins.remove(p)
                break   # una muerte por frame esta bien

        # ── Tick de pinguinos ────────────────────────
        for p in self.penguins:
            p.tick()
            if p._wants_new:
                p._wants_new = False
                if p.row <= 5 and p.col >= 14:
                    nuevo = self._spawn(7, 9)
                    self._push_msg(
                        f"+ {nuevo.nombre} creado!",
                        color=(80, 220, 80), duration_ms=3000)

        # ── Scroll de camara ─────────────────────────
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
        self._draw_event_msgs()
        if self.active_win and self.active_win.active:
            self.active_win.draw(self.screen)
        pygame.display.flip()

    def _draw_hud(self):
        pygame.draw.rect(self.screen, (11, 11, 25), (0, 0, WIN_W, HUD_H))
        pygame.draw.line(self.screen, CUI_CYAN, (0, HUD_H - 1), (WIN_W, HUD_H - 1))

        # Titulo
        self.screen.blit(
            self.font_big.render("CYBORG PENGUINS", True, CUI_CYAN), (10, 4))

        # ── Barra de HAMBRE ─────────────────────────
        h_pct = self.colony.hunger_pct
        h_col  = self.colony.hunger_color()
        BAR_X, BAR_Y, BAR_W, BAR_H2 = 10, 26, 160, 12

        # Fondo
        pygame.draw.rect(self.screen, (40, 20, 20),
                         (BAR_X, BAR_Y, BAR_W, BAR_H2))
        # Relleno
        fill_w = int(h_pct * BAR_W)
        if fill_w > 0:
            pygame.draw.rect(self.screen, h_col,
                             (BAR_X, BAR_Y, fill_w, BAR_H2))
        # Borde
        pygame.draw.rect(self.screen, (100, 50, 50),
                         (BAR_X, BAR_Y, BAR_W, BAR_H2), 1)

        # Label hambre
        hunger_val = int(self.colony.hunger)
        h_label = self.font_sm.render(
            f"Hambre: {hunger_val}/{int(HUNGER_MAX)}", True, CUI_WHITE)
        self.screen.blit(h_label, (BAR_X + BAR_W + 6, BAR_Y))

        # Temporizador del proximo pez consumido
        eat_pct = self.colony.next_eat_pct()
        fish_in_store = self.inventory.obtener("Pez")
        eat_col = (80, 180, 100) if fish_in_store > 0 else (100, 60, 60)
        pygame.draw.rect(self.screen, (20, 30, 20),
                         (BAR_X, BAR_Y + BAR_H2 + 2, BAR_W, 4))
        eat_w = int(eat_pct * BAR_W)
        if eat_w > 0:
            pygame.draw.rect(self.screen, eat_col,
                             (BAR_X, BAR_Y + BAR_H2 + 2, eat_w, 4))
        secs_left = int((1.0 - eat_pct) * 20)
        eat_lbl = self.font_sm.render(
            f"Prox.pez: {secs_left}s  "
            f"({'come' if fish_in_store > 0 else 'sin peces!'})  "
            f"drain x{1.0 + (self.colony.alive_count - 1) * 0.5:.1f}",
            True, eat_col)
        self.screen.blit(eat_lbl, (BAR_X + BAR_W + 6, BAR_Y + BAR_H2 + 1))

        # Advertencia hambre critica
        if h_pct < 0.2:
            t_ms = pygame.time.get_ticks()
            if (t_ms // 400) % 2 == 0:
                warn = self.font_sm.render(
                    "⚠ HAMBRE CRITICA — almacena peces!", True, (255, 80, 80))
                self.screen.blit(warn, (BAR_X, BAR_Y + BAR_H2 + 8))

        # Nidos
        nido_s = self.font_sm.render(
            f"Nidos: {self.colony.nidos}", True, (200, 160, 80))
        self.screen.blit(nido_s, (BAR_X + BAR_W + 90, BAR_Y))

        # Inventario global (derecha)
        inv_s = self.font_sm.render(self.inventory.hud(), True, CUI_GREEN)
        self.screen.blit(inv_s, inv_s.get_rect(right=WIN_W - 8, top=4))

        # Pingüino seleccionado
        sel = next((p for p in self.penguins if p.selected), None)
        if sel:
            zone   = self.world.zone_name(sel.row, sel.col)
            status = " [RUNNING]" if (sel.win and sel.win.running) else ""
            self.screen.blit(
                self.font_sm.render(
                    f"[ {zone} ]  {sel.nombre}{status}",
                    True, CUI_ORANGE),
                (WIN_W - 280, 18))
            self.screen.blit(
                self.font_sm.render(
                    f"Mochila: {sel.inv_status()}", True, (180, 200, 255)),
                (WIN_W - 280, 32))

        # Contador de pinguinos
        alive_cnt = len(self.penguins)
        pc_s = self.font_sm.render(
            f"Pinguinos: {alive_cnt}", True, CUI_WHITE)
        self.screen.blit(pc_s, (WIN_W - 280, 46))

        # Barra inferior
        bar_y = HUD_H + VH * T
        pygame.draw.rect(self.screen, (8, 8, 18), (0, bar_y, WIN_W, BAR_H))
        pygame.draw.line(self.screen, CUI_GRAY, (0, bar_y), (WIN_W, bar_y))
        self.screen.blit(
            self.font_sm.render(
                "Clic pinguino→editor | F5 run | F6 stop | "
                "Flechas→camara | pescar=40% | max mochila=5 | "
                "construir_nido()=50M+100H",
                True, (55, 60, 88)),
            (4, bar_y + 3))

    def _draw_event_msgs(self):
        """Mensajes flotantes de eventos (muertes, creaciones, etc.)."""
        now = pygame.time.get_ticks()
        self._event_msgs = [m for m in self._event_msgs if m[1] > now]
        y = HUD_H + 4
        for text, _, color in self._event_msgs[-4:]:
            s = self.font_sm.render(text, True, color)
            self.screen.blit(s, (WIN_W // 2 - s.get_width() // 2, y))
            y += 16

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
                    s = font.render("Error interno (ver consola)",
                                    True, (220, 60, 60))
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