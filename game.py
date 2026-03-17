# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — game.py  (HUD mejorado, resolución grande)
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import traceback
import pygame

from config import (
    WIN_W, WIN_H, HUD_H, BAR_H,
    VW, VH, WW, WH, T, FPS,
    CUI_BG, CUI_CYAN, CUI_GREEN, CUI_ORANGE, CUI_GRAY, CUI_WHITE, CUI_RED,
    CUI_YELLOW, CUI_PURPLE, CUI_BLUE, CUI_BLACK,
    COMP_POSITIONS,
    HUNGER_MAX,
)
from world import World
from inventory import Inventory
from penguin import Penguin
from colony import Colony
from ui.window import SimulatedPythonWindow
from ui.terminal import ComputerTerminal

CAM_SPEED = 4


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("🐧 Cyborg Penguins")
        self.clock   = pygame.time.Clock()
        self.running = True

        # Fuentes
        self.font_sm  = pygame.font.SysFont("Courier New", 13)
        self.font_md  = pygame.font.SysFont("Courier New", 16)
        self.font_big = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_hud = pygame.font.SysFont("Courier New", 14, bold=True)

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

        self._event_msgs: list[tuple[str, float, tuple]] = []
        self._last_ms = pygame.time.get_ticks()
        self._spawn(7, 9, "Pingu-01")
        self._center_camera()

    # ── Helpers ─────────────────────────────────────────
    def _spawn(self, row, col, nombre=None) -> Penguin:
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

    def _push_msg(self, text, color=(255, 80, 80), duration_ms=3000):
        expire = pygame.time.get_ticks() + duration_ms
        self._event_msgs.append((text, expire, color))
        if len(self._event_msgs) > 6:
            self._event_msgs.pop(0)

    # ── Eventos ─────────────────────────────────────────
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

    # ── Update ──────────────────────────────────────────
    def update(self):
        now    = pygame.time.get_ticks()
        dt_sec = (now - self._last_ms) / 1000.0
        self._last_ms = now

        if self.active_win and not self.active_win.active:
            self.active_win = None

        self.world.update(now)

        victims = self.colony.update(dt_sec, now, self.penguins)
        for p in victims:
            p.alive = False
            p.stop_script()
            if p == next((x for x in self.penguins if x.selected), None):
                alive = [x for x in self.penguins if x.alive]
                if alive:
                    alive[0].selected = True
            self._push_msg(f"☠ {p.nombre} murio de hambre!", (255, 60, 60), 5000)

        for p in self.penguins:
            p.tick()
            if p._wants_new:
                p._wants_new = False
                if p.row <= 5 and p.col >= 14:
                    nuevo = self._spawn(7, 9)
                    self._push_msg(f"+ {nuevo.nombre} creado!", (80, 220, 80), 3000)

        self.penguins = [p for p in self.penguins if p.alive]

        editor_open = self.active_win and self.active_win.active
        if not editor_open:
            self._cam_timer += 1
            if self._cam_timer >= CAM_SPEED:
                self._cam_timer = 0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:  self.cam_col = max(0, self.cam_col - 1)
                if keys[pygame.K_RIGHT]: self.cam_col = min(WW - VW, self.cam_col + 1)
                if keys[pygame.K_UP]:    self.cam_row = max(0, self.cam_row - 1)
                if keys[pygame.K_DOWN]:  self.cam_row = min(WH - VH, self.cam_row + 1)

    # ── Draw ─────────────────────────────────────────────
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

    # ── HUD mejorado ─────────────────────────────────────
    def _draw_hud(self):
        # Fondo con gradiente simulado
        pygame.draw.rect(self.screen, (8, 10, 22), (0, 0, WIN_W, HUD_H))
        pygame.draw.rect(self.screen, (12, 14, 28), (0, 4, WIN_W, HUD_H - 8))
        # Línea inferior con glow
        pygame.draw.line(self.screen, CUI_CYAN,   (0, HUD_H-1), (WIN_W, HUD_H-1))
        pygame.draw.line(self.screen, (0, 80, 80), (0, HUD_H-2), (WIN_W, HUD_H-2))

        # ── Título con efecto ────────────────────────────
        title = self.font_big.render("CYBORG PENGUINS", True, CUI_CYAN)
        # Sombra
        shadow = self.font_big.render("CYBORG PENGUINS", True, (0, 60, 60))
        self.screen.blit(shadow, (12, 6))
        self.screen.blit(title, (10, 4))

        # Subtítulo
        sub = self.font_sm.render("v2.0  |  polar colony sim", True, (60, 120, 120))
        self.screen.blit(sub, (12, 28))

        # ── Barra de HAMBRE ──────────────────────────────
        h_pct  = self.colony.hunger_pct
        h_col  = self.colony.hunger_color()
        BAR_X, BAR_Y, BAR_W, BAR_BH = 12, 46, 180, 14

        # Fondo barra
        pygame.draw.rect(self.screen, (20, 10, 10), (BAR_X-1, BAR_Y-1, BAR_W+2, BAR_BH+2))
        pygame.draw.rect(self.screen, (40, 20, 20), (BAR_X, BAR_Y, BAR_W, BAR_BH))
        fill_w = int(h_pct * BAR_W)
        if fill_w > 0:
            # Barra con brillo superior
            pygame.draw.rect(self.screen, h_col, (BAR_X, BAR_Y, fill_w, BAR_BH))
            bright = tuple(min(255, c + 50) for c in h_col)
            pygame.draw.rect(self.screen, bright, (BAR_X, BAR_Y, fill_w, 3))
        # Segmentos estilo GBA
        for sx in range(0, BAR_W, 12):
            pygame.draw.line(self.screen, (0,0,0), (BAR_X+sx, BAR_Y), (BAR_X+sx, BAR_Y+BAR_BH))
        pygame.draw.rect(self.screen, (80, 40, 40), (BAR_X, BAR_Y, BAR_W, BAR_BH), 1)

        hunger_val = int(self.colony.hunger)
        h_label = self.font_sm.render(
            f"♥ {hunger_val}/{int(HUNGER_MAX)}", True,
            CUI_WHITE if h_pct > 0.25 else CUI_RED)
        self.screen.blit(h_label, (BAR_X + BAR_W + 8, BAR_Y))

        # Temporizador pez
        eat_pct  = self.colony.next_eat_pct()
        fish_cnt = self.inventory.obtener("Pez")
        eat_col  = (80, 200, 100) if fish_cnt > 0 else (160, 60, 60)
        FISH_BAR_X = BAR_X
        FISH_BAR_Y = BAR_Y + BAR_BH + 4
        pygame.draw.rect(self.screen, (16, 28, 16), (FISH_BAR_X, FISH_BAR_Y, BAR_W, 5))
        fw = int(eat_pct * BAR_W)
        if fw > 0:
            pygame.draw.rect(self.screen, eat_col, (FISH_BAR_X, FISH_BAR_Y, fw, 5))
        secs_left = int((1.0 - eat_pct) * 20)
        drain_mult = 1.0 + (self.colony.alive_count - 1) * 0.5
        eat_lbl = self.font_sm.render(
            f"▶{secs_left}s {'🐟' if fish_cnt>0 else 'SIN PECES!'}"
            f"  x{drain_mult:.1f}  Nidos:{self.colony.nidos}",
            True, eat_col)
        self.screen.blit(eat_lbl, (FISH_BAR_X + BAR_W + 8, FISH_BAR_Y - 2))

        # Advertencia crítica parpadeante
        if h_pct < 0.2 and (pygame.time.get_ticks() // 400) % 2 == 0:
            warn = self.font_hud.render("⚠ HAMBRE CRITICA!", True, CUI_RED)
            self.screen.blit(warn, (BAR_X, FISH_BAR_Y + 8))

        # ── Inventario global ────────────────────────────
        # Panel separador
        sep_x = WIN_W // 2 - 60
        pygame.draw.line(self.screen, (40, 44, 80), (sep_x, 8), (sep_x, HUD_H-8))

        inv_items = [
            ("🐟 Pez",    self.inventory.obtener("Pez"),    (80, 160, 255)),
            ("🪵 Madera", self.inventory.obtener("Madera"), (160, 100, 40)),
            ("🧊 Hielo",  self.inventory.obtener("Hielo"),  (180, 230, 255)),
        ]
        inv_x = sep_x + 16
        for label, qty, col in inv_items:
            full_label = f"{label}: {qty}/500"
            s = self.font_hud.render(full_label, True, col)
            self.screen.blit(s, (inv_x, 10))
            # Mini barra de recurso
            bpct = qty / 500
            pygame.draw.rect(self.screen, (24, 24, 40), (inv_x, 26, 80, 4))
            bw = int(bpct * 80)
            if bw > 0:
                pygame.draw.rect(self.screen, col, (inv_x, 26, bw, 4))
            inv_x += 110

        # ── Pingüino seleccionado ────────────────────────
        sel = next((p for p in self.penguins if p.selected), None)
        panel_x = WIN_W - 290
        pygame.draw.line(self.screen, (40, 44, 80), (panel_x - 10, 8), (panel_x - 10, HUD_H-8))

        if sel:
            zone   = self.world.zone_name(sel.row, sel.col)
            status = " [RUNNING]" if (sel.win and sel.win.running) else ""
            # Nombre con color del pingüino
            name_s = self.font_hud.render(f"▶ {sel.nombre}{status}", True, sel.color)
            self.screen.blit(name_s, (panel_x, 6))
            # Zona
            zone_s = self.font_sm.render(f"📍 {zone}", True, CUI_CYAN)
            self.screen.blit(zone_s, (panel_x, 22))
            # Mochila
            mochila = self.font_sm.render(f"🎒 {sel.inv_status()}", True, (180, 200, 255))
            self.screen.blit(mochila, (panel_x, 36))
            # Cantidad de pingüinos
            cnt_s = self.font_sm.render(
                f"🐧 x{len(self.penguins)}  | Clic→editor | F5 run | F6 stop",
                True, (100, 110, 160))
            self.screen.blit(cnt_s, (panel_x, 52))
        else:
            hint = self.font_sm.render("← Clic en un pingüino para seleccionarlo", True, CUI_GRAY)
            self.screen.blit(hint, (panel_x, 20))
            cnt_s = self.font_sm.render(f"Pingüinos: {len(self.penguins)}", True, CUI_WHITE)
            self.screen.blit(cnt_s, (panel_x, 38))

        # ── Barra inferior ───────────────────────────────
        bar_y = HUD_H + VH * T
        pygame.draw.rect(self.screen, (6, 8, 18), (0, bar_y, WIN_W, BAR_H))
        pygame.draw.line(self.screen, (40, 44, 80), (0, bar_y), (WIN_W, bar_y))
        help_txt = (
            "⬆⬇⬅➡ cámara  |  clic pingüino → editor Python  |  "
            "pescar() · talar() · picar_hielo() · almacenar('X') · construir_nido() · crear_pinguino()"
        )
        help_s = self.font_sm.render(help_txt, True, (56, 62, 96))
        self.screen.blit(help_s, (6, bar_y + 4))

    # ── Mensajes flotantes ───────────────────────────────
    def _draw_event_msgs(self):
        now = pygame.time.get_ticks()
        self._event_msgs = [m for m in self._event_msgs if m[1] > now]
        y = HUD_H + 6
        for text, _, color in self._event_msgs[-4:]:
            # Fondo semitransparente
            s = self.font_hud.render(text, True, color)
            bg = pygame.Surface((s.get_width() + 12, s.get_height() + 4))
            bg.fill((8, 10, 20))
            bg.set_alpha(200)
            cx = WIN_W // 2 - (s.get_width() + 12) // 2
            self.screen.blit(bg, (cx, y - 2))
            # Borde del color del mensaje
            pygame.draw.rect(self.screen, color,
                             (cx, y-2, s.get_width()+12, s.get_height()+4), 1)
            self.screen.blit(s, (cx + 6, y))
            y += s.get_height() + 6

    # ── Loop ─────────────────────────────────────────────
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
                    s = self.font_sm.render("Error interno (ver consola)", True, (220, 60, 60))
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
