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
from world import World, Tile, clear_tile_cache
from inventory import Inventory
from penguin import Penguin
from colony import Colony
from ui.window import SimulatedPythonWindow
from ui.terminal import ComputerTerminal
from ui.intro import IntroScreen
from ui.menu import MainMenu
from progress import ProgressTracker
from save import save_game, load_game, save_exists

CAM_SPEED   = 4
ZOOM_LEVELS = [16, 24, 32, 48, 64, 80]   # tamaños de tile disponibles
MAP_PADDING = 10                  # tiles oscuros navegables fuera del mapa


class Game:
    def __init__(self):
        pygame.init()
        self._fullscreen = False
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("🐧 The Penguin Was Replace")
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

        # Progress tracker — conectado a la primera PC (zona pesca)
        self.progress = ProgressTracker()
        self.progress.terminal = self.computers[0]

        self.penguins:    list[Penguin]                = []
        self.active_win:  SimulatedPythonWindow | None = None
        self.active_comp: ComputerTerminal | None      = None

        self.cam_col    = 0
        self.cam_row    = 0
        self._cam_timer = 0
        self._zoom_idx  = 4           # índice en ZOOM_LEVELS → empieza en T=64

        self._event_msgs: list[tuple[str, float, tuple]] = []
        self._obj_notif: tuple | None = None   # (linea1, linea2, expire_ms)
        self._last_ms = pygame.time.get_ticks()
        self._intro = IntroScreen()
        self._menu  = MainMenu()
        self._state = "menu"   # "menu" | "intro" | "game"
        self.progress.on_unlock = self._on_objective_unlocked
        self._spawn(7, 9, "Pingu-01")
        self._center_camera()

    # ── Zoom ─────────────────────────────────────────────
    @property
    def T(self) -> int:
        return ZOOM_LEVELS[self._zoom_idx]

    @property
    def VW(self) -> int:
        return WIN_W // self.T

    @property
    def VH(self) -> int:
        return (WIN_H - HUD_H - BAR_H) // self.T

    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.screen = pygame.display.set_mode(
                (WIN_W, WIN_H), pygame.SCALED | pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIN_W, WIN_H))

    def _zoom_in(self):
        if self._zoom_idx < len(ZOOM_LEVELS) - 1:
            self._zoom_idx += 1
            clear_tile_cache()
            self._clamp_camera()

    def _zoom_out(self):
        if self._zoom_idx > 0:
            self._zoom_idx -= 1
            clear_tile_cache()
            self._clamp_camera()

    def _clamp_camera(self):
        # Si el mapa entra entero en la pantalla → centrarlo
        # Si no → scroll libre con MAP_PADDING tiles oscuros de margen
        if self.VW >= WW:
            self.cam_col = -((self.VW - WW) // 2)
        else:
            self.cam_col = max(-MAP_PADDING,
                               min(self.cam_col, WW - self.VW + MAP_PADDING))
        if self.VH >= WH:
            self.cam_row = -((self.VH - WH) // 2)
        else:
            self.cam_row = max(-MAP_PADDING,
                               min(self.cam_row, WH - self.VH + MAP_PADDING))

    # ── Notificaciones de objetivo ───────────────────────
    _OBJECTIVE_NAMES = {
        "tutorial_bash.txt":  ("PC REPARADA",          "Lee el tutorial en la terminal"),
        "pescar.vim":         ("COMANDOS DISPONIBLES",  "Referencia rapida de comandos"),
        "while_loops.txt":    ("OBJETIVO 2",            "Aprende los bucles — while True"),
        "almacenar.txt":      ("ALMACEN CENTRAL ON",    "Guarda recursos en el almacen"),
        "talar.txt":          ("BOSQUE GLACIAL ON",     "Tala arboles para conseguir madera"),
        "picar_hielo.txt":    ("MINA DE HIELO ON",      "Extrae hielo del subsuelo"),
        "construir_nido.txt": ("ZONA DE CONSTRUCCION",  "Construi tu primer iglu"),
        "crear_pinguino.txt": ("REPRODUCCION HABILITADA","Crea nuevos pinguinos cyborg"),
        "transmision_final.txt": ("MISION COMPLETADA!", "La colonia sobrevive"),
    }

    _ZONE_UNLOCKS = {
        "almacenar.txt":      ["f_almacen"],
        "talar.txt":          ["f_bosque"],
        "picar_hielo.txt":    ["f_mina"],
        "construir_nido.txt": ["f_fabrica"],
    }

    def _on_objective_unlocked(self, filename: str):
        title, desc = self._OBJECTIVE_NAMES.get(
            filename, ("NUEVO OBJETIVO", filename))
        expire = pygame.time.get_ticks() + 5000
        self._obj_notif = (title, desc, expire)

        for zone in self._ZONE_UNLOCKS.get(filename, []):
            self.world.unlock_zone(zone)

    # ── Helpers ─────────────────────────────────────────
    def _spawn(self, row, col, nombre=None) -> Penguin:
        p = Penguin(nombre=nombre, row=row, col=col,
                    world=self.world, inventory=self.inventory,
                    colony=self.colony)
        p.progress = self.progress   # para notificar peces pescados
        self.penguins.append(p)
        return p

    def _center_camera(self):
        target = next((p for p in self.penguins if p.selected and p.alive),
                      next((p for p in self.penguins if p.alive), None))
        if target:
            self.cam_col = target.col - self.VW // 2
            self.cam_row = target.row - self.VH // 2
            self._clamp_camera()

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = "menu"
                    self._menu.reset_sel()
                    continue
                if event.key == pygame.K_f:
                    self._toggle_fullscreen()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self._zoom_in()
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self._zoom_out()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(event.pos)

    def _on_click(self, pos):
        mx, my = pos
        if my < HUD_H or my >= HUD_H + self.VH * self.T:
            return
        wc = self.cam_col + mx // self.T
        wr = self.cam_row + (my - HUD_H) // self.T
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
                comp.on_open()
                self._obj_notif = None
                return

    # ── Update ──────────────────────────────────────────
    def update(self):
        now    = pygame.time.get_ticks()
        dt_sec = (now - self._last_ms) / 1000.0
        self._last_ms = now

        if self.active_win and not self.active_win.active:
            self.active_win = None

        self.world.update(now)

        # Desbloqueo de archivos segun progreso
        inv = self.inventory
        self.progress.check_storage(
            inv.obtener("Pez"),
            inv.obtener("Madera"),
            inv.obtener("Hielo"),
        )
        # Detectar cuando la PC fue reparada (bash activo)
        pc = self.computers[0]
        if pc.estado == "bash" and "tutorial_bash.txt" not in pc._unlocked_files:
            self.progress.on_pc_repaired()

        # ── Hambre ──────────────────────────────────
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
                    self.progress.on_penguin_created(len(self.penguins))

        self.penguins = [p for p in self.penguins if p.alive]

        editor_open = self.active_win and self.active_win.active
        if not editor_open:
            self._cam_timer += 1
            if self._cam_timer >= CAM_SPEED:
                self._cam_timer = 0
                keys = pygame.key.get_pressed()
                moved = False
                if keys[pygame.K_LEFT]:  self.cam_col -= 1; moved = True
                if keys[pygame.K_RIGHT]: self.cam_col += 1; moved = True
                if keys[pygame.K_UP]:    self.cam_row -= 1; moved = True
                if keys[pygame.K_DOWN]:  self.cam_row += 1; moved = True
                if moved:
                    self._clamp_camera()

    # ── Draw ─────────────────────────────────────────────
    def draw(self):
        self.screen.fill(CUI_BG)
        self.world.draw(self.screen, self.cam_col, self.cam_row, self.font_sm,
                        tile_size=self.T, vw=self.VW, vh=self.VH)
        for p in self.penguins:
            p.draw(self.screen, self.cam_col, self.cam_row, self.font_sm,
                   tile_size=self.T, vw=self.VW, vh=self.VH)
        for comp in self.computers:
            comp.draw(self.screen, self.font_sm)
            if not comp.show:
                comp.draw_world_indicator(self.screen, self.cam_col, self.cam_row,
                                          self.font_sm, self.T, self.VW, self.VH, HUD_H)
        self._draw_hud()
        if not (self.active_comp and self.active_comp.show):
            self._draw_obj_notif()
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
        title = self.font_big.render("THE PENGUIN WAS REPLACE", True, CUI_CYAN)
        # Sombra
        shadow = self.font_big.render("THE PENGUIN WAS REPLACE", True, (0, 60, 60))
        self.screen.blit(shadow, (12, 6))
        self.screen.blit(title, (10, 4))

        # Subtítulo
        sub = self.font_sm.render("hackathon edition", True, (60, 120, 120))
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

        # Advertencia crítica parpadeante (reemplaza el subtítulo)
        if h_pct < 0.2 and (pygame.time.get_ticks() // 400) % 2 == 0:
            warn = self.font_hud.render("⚠ HAMBRE CRITICA!", True, CUI_RED)
            self.screen.blit(warn, (BAR_X, 28))

        # ── Inventario global (columna vertical) ─────────
        sep_x = WIN_W // 3
        pygame.draw.line(self.screen, (40, 44, 80), (sep_x, 8), (sep_x, HUD_H-8))

        inv_items = [
            ("🐟 Pez",    self.inventory.obtener("Pez"),    (80, 160, 255)),
            ("🪵 Madera", self.inventory.obtener("Madera"), (160, 100, 40)),
            ("🧊 Hielo",  self.inventory.obtener("Hielo"),  (180, 230, 255)),
        ]
        inv_x = sep_x + 14
        for i, (label, qty, col) in enumerate(inv_items):
            y = 7 + i * 23
            s = self.font_hud.render(f"{label}: {qty}/500", True, col)
            self.screen.blit(s, (inv_x, y))

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
                f"🐧 x{len(self.penguins)}  | Clic→editor | F5 ejecutar | F6 detener",
                True, (100, 110, 160))
            self.screen.blit(cnt_s, (panel_x, 52))
        else:
            hint = self.font_sm.render("← Clic en un pingüino para seleccionarlo", True, CUI_GRAY)
            self.screen.blit(hint, (panel_x, 20))
            cnt_s = self.font_sm.render(f"Pingüinos: {len(self.penguins)}", True, CUI_WHITE)
            self.screen.blit(cnt_s, (panel_x, 38))

        # ── Banner "!" objetivo sin leer ────────────────
        if any(c.has_unread for c in self.computers):
            if (pygame.time.get_ticks() // 450) % 2 == 0:
                notif_s = self.font_hud.render(
                    "!  NUEVO OBJETIVO  —  Acercate a la PC",
                    True, (255, 180, 0))
                nx = WIN_W // 2 - notif_s.get_width() // 2
                bg = pygame.Surface((notif_s.get_width() + 16, notif_s.get_height() + 4))
                bg.fill((40, 20, 0))
                bg.set_alpha(220)
                self.screen.blit(bg, (nx - 8, HUD_H - notif_s.get_height() - 6))
                pygame.draw.rect(self.screen, (200, 100, 0),
                                 (nx - 8, HUD_H - notif_s.get_height() - 6,
                                  notif_s.get_width() + 16, notif_s.get_height() + 4), 1)
                self.screen.blit(notif_s, (nx, HUD_H - notif_s.get_height() - 4))

        # ── Barra inferior ───────────────────────────────
        bar_y = WIN_H - BAR_H
        pygame.draw.rect(self.screen, (6, 8, 18), (0, bar_y, WIN_W, BAR_H))
        pygame.draw.line(self.screen, (40, 44, 80), (0, bar_y), (WIN_W, bar_y))
        help_txt = (
            "⬆⬇⬅➡ cámara  |  clic pingüino → editor Python  |  "
            "pescar() · talar() · picar_hielo() · almacenar('X') · construir_nido() · crear_pinguino()"
        )
        help_s = self.font_sm.render(help_txt, True, (56, 62, 96))
        self.screen.blit(help_s, (6, bar_y + 4))

    # ── Popup de objetivo desbloqueado ───────────────────
    def _draw_obj_notif(self):
        if not self._obj_notif:
            return
        title, desc, expire = self._obj_notif
        now = pygame.time.get_ticks()
        if now > expire:
            self._obj_notif = None
            return

        # Fade out en el último segundo
        remaining = expire - now
        alpha = min(255, int(remaining / 300 * 255))

        W, H = 380, 66
        x = WIN_W // 2 - W // 2
        y = HUD_H + 12

        bg = pygame.Surface((W, H), pygame.SRCALPHA)
        bg.fill((10, 16, 30, min(alpha, 220)))
        self.screen.blit(bg, (x, y))

        border_col = tuple(int(c * alpha / 255) for c in (0, 200, 200))
        pygame.draw.rect(self.screen, border_col, (x, y, W, H), 2)

        # Barra izquierda de acento
        accent = tuple(int(c * alpha / 255) for c in (255, 160, 0))
        pygame.draw.rect(self.screen, accent, (x, y, 4, H))

        title_col = tuple(int(c * alpha / 255) for c in (255, 200, 60))
        desc_col  = tuple(int(c * alpha / 255) for c in (180, 210, 240))

        self.screen.blit(
            self.font_hud.render(f"  {title}", True, title_col),
            (x + 10, y + 10))
        self.screen.blit(
            self.font_sm.render(f"  {desc}", True, desc_col),
            (x + 10, y + 32))
        self.screen.blit(
            self.font_sm.render("  Abrí la PC para ver el objetivo completo",
                                True, tuple(int(c * alpha / 255) for c in (80, 100, 140))),
            (x + 10, y + 48))

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

    # ── Guardar / Cargar ─────────────────────────────────
    def _do_save(self):
        ok = save_game(self)
        self._menu.set_message("Partida guardada!" if ok else "Error al guardar.", ok=ok)

    def _do_load(self):
        data = load_game()
        if data is None:
            self._menu.set_message("No hay partida guardada.", ok=False)
            return
        self._apply_save(data)
        self._state = "game"
        self._menu.game_active = True

    def _apply_save(self, data: dict):
        # Detener scripts actuales
        for p in self.penguins:
            p.stop_script()
        self.penguins = []

        # Cámara
        self.cam_col = data.get("cam_col", 0)
        self.cam_row = data.get("cam_row", 0)

        # Inventario
        for nombre, qty in data.get("inventory", {}).items():
            r = self.inventory.rs.get(nombre)
            if r:
                r.cantidad = qty

        # Progreso
        prog = data.get("progress", {})
        self.progress.fish_caught_total = prog.get("fish_caught_total", 0)
        self.progress._unlocked = set(prog.get("unlocked", []))

        # Mundo: zonas + nidos
        world_data = data.get("world", {})
        self.world.unlocked_zones = set(
            world_data.get("unlocked_zones", ["f_pesca", "costa", "agua"]))
        for r, c in world_data.get("nidos", []):
            self.world.grid[r][c] = Tile("nido")

        # Colonia
        col = data.get("colony", {})
        self.colony.hunger = col.get("hunger", 100.0)
        self.colony.nidos  = col.get("nidos", 0)

        # Pingüinos
        for pd in data.get("penguins", []):
            p = self._spawn(pd["row"], pd["col"], pd["nombre"])
            script = pd.get("script", "").strip()
            if script:
                p.win = SimulatedPythonWindow(p)
                p.win.lines   = script.split("\n")
                p.win.cur_ln  = 0
                p.win.cur_col = 0
                if pd.get("running", False):
                    p.win._run()

        # Terminal
        term = data.get("terminal", {})
        comp = self.computers[0]
        comp.estado          = term.get("estado", "offline")
        comp._unlocked_files = set(term.get("unlocked_files", []))
        self.progress.terminal = comp

        self._clamp_camera()

    # ── Loop ─────────────────────────────────────────────
    def run(self):
        while self.running:
            try:
                if self._state == "menu":
                    self._run_menu_frame()
                elif self._state == "intro":
                    self._run_intro_frame()
                else:
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

    def _run_menu_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
                return
            action = self._menu.handle_event(event)
            if action == "start":
                self._intro = IntroScreen()
                self._state = "intro"
                self._menu.game_active = True
            elif action == "continue":
                self._state = "game"
            elif action == "save":
                if self._menu.game_active:
                    self._do_save()
                else:
                    self._menu.set_message("Inicia una partida primero.", ok=False)
            elif action == "load":
                self._do_load()
            elif action == "exit":
                self._quit()
        self._menu.draw(self.screen)
        pygame.display.flip()

    def _run_intro_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
                return
            done = self._intro.handle_event(event)
            if done:
                self._state = "game"
        if self._intro.done:
            self._state = "game"
        else:
            self._intro.draw(self.screen)
            pygame.display.flip()

    def _quit(self):
        for p in self.penguins:
            p.stop_script()
        pygame.quit()
        import sys; sys.exit()
