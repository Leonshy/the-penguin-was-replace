# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — ui/window.py
#  Ventana Python simulada (editor + output + autocomplete)
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import re
import pygame

from config import (
    WIN_W, WIN_H,
    IDE_BG, IDE_DARK, IDE_TITLE, IDE_HL, IDE_LNBG,
    IDE_BORDER, IDE_CURSOR, IDE_SEP, IDE_OUT,
    SYN_OK, SYN_ERR,
    CUI_WHITE, CUI_GRAY,
    AC_BG, AC_BORDER, AC_SEL_BG, AC_DOC_BG,
    AC_ITEM_H, AC_MAX_VIS, AC_DROP_W, AC_DOC_W,
    AC_KIND_STYLE,
)
from ui.autocomplete import AC_DB, tokenize

_LINE_H  = 19
_CHAR_W  = 8
_LNPAD   = 38
_EPAD    = 6
_FONT_SZ = 14


class SimulatedPythonWindow:
    """
    Ventana de codigo Python simulada en pygame.

    Novedades:
    - Boton STOP: detiene el script en curso (incluso bucles infinitos)
    - Indicador "RUNNING..." mientras el script corre
    - Output se actualiza en vivo desde el hilo del script
    """

    W            = 640
    TITLE_H      = 26
    TOOLBAR_H    = 30
    EDITOR_LINES = 14
    EDITOR_H     = EDITOR_LINES * _LINE_H + _EPAD * 2
    SEP_H        = 2
    OUT_HDR_H    = 18
    OUT_LINES    = 8
    OUT_H        = OUT_LINES * _LINE_H + 8
    STATUS_H     = 18
    H = TITLE_H + TOOLBAR_H + EDITOR_H + SEP_H + OUT_HDR_H + OUT_H + STATUS_H

    def __init__(self, penguin, x: int = 50, y: int = 110):
        self.penguin  = penguin
        self.rect     = pygame.Rect(x, y, self.W, self.H)
        self.active   = True
        self.running  = False   # True mientras el script corre en hilo

        self.lines:    list[str]         = [""]
        self.cur_ln:   int               = 0
        self.cur_col:  int               = 0
        self.scroll:   int               = 0

        self.out: list[tuple[str, str]]  = []

        self._drag = False
        self._dox  = 0
        self._doy  = 0

        self.ac_items:   list[dict] = []
        self.ac_idx:     int        = 0
        self.ac_scroll:  int        = 0
        self.ac_visible: bool       = False

        self._fonts_ok = False
        self.font_code = None
        self.font_ui   = None
        self.font_sm   = None
        self.font_ac   = None

    # ── Fuentes ─────────────────────────────────────
    def _init_fonts(self):
        if self._fonts_ok:
            return
        self.font_code = pygame.font.SysFont("Courier New", _FONT_SZ)
        self.font_ui   = pygame.font.SysFont("Courier New", _FONT_SZ)
        self.font_sm   = pygame.font.SysFont("Courier New", 11)
        self.font_ac   = pygame.font.SysFont("Courier New", 12)
        global _CHAR_W
        _CHAR_W = self.font_code.size("X")[0]
        self._fonts_ok = True

    # ── Geometria ────────────────────────────────────
    @property
    def _r_title(self):
        return pygame.Rect(self.rect.x, self.rect.y, self.W, self.TITLE_H)
    @property
    def _r_toolbar(self):
        return pygame.Rect(self.rect.x, self.rect.y + self.TITLE_H,
                           self.W, self.TOOLBAR_H)
    @property
    def _r_editor(self):
        y = self.rect.y + self.TITLE_H + self.TOOLBAR_H
        return pygame.Rect(self.rect.x, y, self.W, self.EDITOR_H)
    @property
    def _r_output(self):
        y = (self.rect.y + self.TITLE_H + self.TOOLBAR_H
             + self.EDITOR_H + self.SEP_H + self.OUT_HDR_H)
        return pygame.Rect(self.rect.x, y, self.W, self.OUT_H)
    @property
    def _r_status(self):
        return pygame.Rect(self.rect.x, self._r_output.bottom,
                           self.W, self.STATUS_H)

    # ── Scroll ───────────────────────────────────────
    def _clamp_scroll(self):
        if self.cur_ln < self.scroll:
            self.scroll = self.cur_ln
        elif self.cur_ln >= self.scroll + self.EDITOR_LINES:
            self.scroll = self.cur_ln - self.EDITOR_LINES + 1
        self.scroll = max(0, self.scroll)

    # ── Eventos ──────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> bool:
        self._init_fonts()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # X cerrar
            close = pygame.Rect(self.rect.right - 27,
                                 self._r_title.y + 4, 22,
                                 self.TITLE_H - 8)
            if close.collidepoint(mx, my):
                self.active = False; return True
            # Drag titulo
            if self._r_title.collidepoint(mx, my):
                self._drag = True
                self._dox, self._doy = mx - self.rect.x, my - self.rect.y
                return True
            # Toolbar
            if self._r_toolbar.collidepoint(mx, my):
                self._toolbar_click(mx, my); return True
            # Click en editor
            er = self._r_editor
            if er.collidepoint(mx, my):
                rel_y = my - er.y - _EPAD
                rel_x = mx - er.x - _LNPAD - _EPAD
                cl = max(0, min(self.scroll + rel_y // _LINE_H,
                                len(self.lines) - 1))
                cc = max(0, min(rel_x // max(_CHAR_W, 1),
                                len(self.lines[cl])))
                self.cur_ln, self.cur_col = cl, cc
                return True
            if not self.rect.collidepoint(mx, my):
                return False

        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag = False

        elif event.type == pygame.MOUSEMOTION:
            if self._drag:
                mx, my = event.pos
                nx = max(0, min(mx - self._dox, WIN_W - self.W))
                ny = max(0, min(my - self._doy, WIN_H - self.H))
                self.rect.x, self.rect.y = nx, ny

        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)
            return True

        return False

    # ── Toolbar ──────────────────────────────────────
    def _toolbar_click(self, mx: int, my: int):
        bx = self.rect.x + 8
        if bx <= mx <= bx + 126:
            self._run()
        elif bx + 134 <= mx <= bx + 134 + 72:
            self._stop()
        elif bx + 214 <= mx <= bx + 214 + 72:
            self._clear()

    # ── Teclado ──────────────────────────────────────
    def _handle_key(self, event: pygame.event.Event):
        k, mod = event.key, event.mod

        if k == pygame.K_ESCAPE:
            if self.ac_visible:
                self.ac_visible = False; return
            self.active = False; return

        if k == pygame.K_SPACE and (mod & pygame.KMOD_CTRL):
            self._update_ac(); return

        if self.ac_visible and self.ac_items:
            if k == pygame.K_DOWN:
                self.ac_idx = (self.ac_idx + 1) % len(self.ac_items)
                self._clamp_ac_scroll(); return
            if k == pygame.K_UP:
                self.ac_idx = (self.ac_idx - 1) % len(self.ac_items)
                self._clamp_ac_scroll(); return
            if k in (pygame.K_TAB, pygame.K_RETURN):
                self._accept_ac(); return
            if k == pygame.K_ESCAPE:
                self.ac_visible = False; return

        if k == pygame.K_F5 or (k == pygame.K_RETURN and (mod & pygame.KMOD_CTRL)):
            self.ac_visible = False
            self._run(); return

        if k == pygame.K_F6:
            self._stop(); return

        if k == pygame.K_RETURN:
            self.ac_visible = False
            curr   = self.lines[self.cur_ln]
            indent = len(curr) - len(curr.lstrip(' '))
            if curr.rstrip().endswith(':'):
                indent += 4
            rest = curr[self.cur_col:]
            self.lines[self.cur_ln] = curr[:self.cur_col]
            self.lines.insert(self.cur_ln + 1, ' ' * indent + rest)
            self.cur_ln += 1; self.cur_col = indent
            self._clamp_scroll(); return

        if k == pygame.K_BACKSPACE:
            if self.cur_col > 0:
                l = self.lines[self.cur_ln]
                self.lines[self.cur_ln] = l[:self.cur_col-1] + l[self.cur_col:]
                self.cur_col -= 1
            elif self.cur_ln > 0:
                prev = self.lines[self.cur_ln - 1]
                self.cur_col = len(prev)
                self.lines[self.cur_ln - 1] = prev + self.lines[self.cur_ln]
                self.lines.pop(self.cur_ln)
                self.cur_ln -= 1
            self._clamp_scroll(); self._update_ac(); return

        if k == pygame.K_DELETE:
            l = self.lines[self.cur_ln]
            if self.cur_col < len(l):
                self.lines[self.cur_ln] = l[:self.cur_col] + l[self.cur_col+1:]
            elif self.cur_ln < len(self.lines) - 1:
                self.lines[self.cur_ln] += self.lines[self.cur_ln + 1]
                self.lines.pop(self.cur_ln + 1)
            self._update_ac(); return

        if k == pygame.K_TAB:
            if self.ac_visible and self.ac_items:
                self._accept_ac()
            else:
                l = self.lines[self.cur_ln]
                self.lines[self.cur_ln] = l[:self.cur_col] + '    ' + l[self.cur_col:]
                self.cur_col += 4
            return

        if k == pygame.K_UP:
            if self.cur_ln > 0:
                self.cur_ln -= 1
                self.cur_col = min(self.cur_col, len(self.lines[self.cur_ln]))
            self._clamp_scroll(); return
        if k == pygame.K_DOWN:
            if self.cur_ln < len(self.lines) - 1:
                self.cur_ln += 1
                self.cur_col = min(self.cur_col, len(self.lines[self.cur_ln]))
            self._clamp_scroll(); return
        if k == pygame.K_LEFT:
            if self.cur_col > 0:
                self.cur_col -= 1
            elif self.cur_ln > 0:
                self.cur_ln -= 1
                self.cur_col = len(self.lines[self.cur_ln])
            self.ac_visible = False; self._clamp_scroll(); return
        if k == pygame.K_RIGHT:
            l = self.lines[self.cur_ln]
            if self.cur_col < len(l):
                self.cur_col += 1
            elif self.cur_ln < len(self.lines) - 1:
                self.cur_ln += 1; self.cur_col = 0
            self.ac_visible = False; self._clamp_scroll(); return
        if k == pygame.K_HOME:
            self.cur_col = 0; self.ac_visible = False; return
        if k == pygame.K_END:
            self.cur_col = len(self.lines[self.cur_ln])
            self.ac_visible = False; return

        if event.unicode and event.unicode.isprintable():
            l = self.lines[self.cur_ln]
            self.lines[self.cur_ln] = (l[:self.cur_col]
                                       + event.unicode
                                       + l[self.cur_col:])
            self.cur_col += 1
            if event.unicode.isalpha() or event.unicode in ('_', '(', "'", '"'):
                self._update_ac()
            else:
                self.ac_visible = False

    # ── Acciones ─────────────────────────────────────
    def _run(self):
        code = "\n".join(self.lines).strip()
        if not code:
            self.out = [("(sin codigo)", "ok")]; return
        self.out     = [("Ejecutando...", "ok")]
        self.running = True
        self.penguin.interp.run(code)

    def _stop(self):
        if self.running:
            self.penguin.stop_script()
            self.running = False
            self.out.append(("Script detenido por el usuario.", "ok"))

    def _clear(self):
        self.lines    = [""]
        self.cur_ln   = self.cur_col = self.scroll = 0
        self.out      = []
        self.ac_visible = False

    # ── Autocomplete ─────────────────────────────────
    def _word_before_cursor(self) -> str:
        line = self.lines[self.cur_ln]
        i = self.cur_col
        while i > 0 and (line[i-1].isalnum() or line[i-1] == '_'):
            i -= 1
        return line[i:self.cur_col]

    def _word_start_col(self) -> int:
        line = self.lines[self.cur_ln]
        i = self.cur_col
        while i > 0 and (line[i-1].isalnum() or line[i-1] == '_'):
            i -= 1
        return i

    def _detect_param_context(self, line: str, col: int) -> str | None:
        seg = line[:col]
        for fn in ("almacenar",):
            idx = seg.rfind(fn + "(")
            if idx == -1: continue
            after = seg[idx + len(fn) + 1:]
            if ")" not in after:
                return fn
        return None

    def _inner_string_word(self, line: str, col: int) -> str:
        seg = line[:col]
        for ch in reversed(seg):
            if ch in ("(", ",", "'", '"'):
                start = seg.rfind(ch) + 1
                return seg[start:].strip(" '\"")
        return ""

    def _user_defined_symbols(self) -> list[dict]:
        symbols, seen = [], set()
        code = "\n".join(self.lines)
        for m in re.finditer(r'\bdef\s+([a-zA-Z_]\w*)', code):
            n = m.group(1)
            if n not in seen:
                seen.add(n)
                symbols.append({
                    "label": n, "kind": "fn",
                    "insert": f"{n}()", "detail": f"def {n}()",
                    "doc": "Funcion definida por el usuario.",
                })
        for m in re.finditer(r'^[ \t]*([a-zA-Z_]\w*)\s*=',
                              code, re.MULTILINE):
            n = m.group(1)
            if n not in seen and n not in ('True', 'False', 'None'):
                seen.add(n)
                symbols.append({
                    "label": n, "kind": "kw",
                    "insert": n, "detail": n,
                    "doc": "Variable definida por el usuario.",
                })
        return symbols

    def _update_ac(self):
        line = self.lines[self.cur_ln]
        col  = self.cur_col
        param_ctx = self._detect_param_context(line, col)
        if param_ctx == "almacenar":
            inner = self._inner_string_word(line, col)
            candidates = [it for it in AC_DB if it.get("_param_of") == "almacenar"]
            if inner:
                candidates = [it for it in candidates
                              if it["label"].lower().strip("'").startswith(inner.lower())]
            self.ac_items   = candidates
            self.ac_idx     = 0; self.ac_scroll = 0
            self.ac_visible = bool(candidates); return

        word = self._word_before_cursor()
        if not word:
            self.ac_visible = False; self.ac_items = []; return
        prefix    = word.lower()
        base      = [it for it in AC_DB if not it.get("_param_of")]
        all_items = base + self._user_defined_symbols()
        seen, filtered = set(), []
        for it in all_items:
            lbl = it["label"]
            if lbl in seen: continue
            if lbl.lower().startswith(prefix):
                seen.add(lbl); filtered.append(it)
        filtered.sort(key=lambda x: (not x["label"].lower().startswith(prefix),
                                     x["label"]))
        self.ac_items   = filtered
        self.ac_idx     = 0; self.ac_scroll = 0
        self.ac_visible = bool(filtered)

    def _clamp_ac_scroll(self):
        if self.ac_idx < self.ac_scroll:
            self.ac_scroll = self.ac_idx
        elif self.ac_idx >= self.ac_scroll + AC_MAX_VIS:
            self.ac_scroll = self.ac_idx - AC_MAX_VIS + 1

    def _accept_ac(self):
        if not self.ac_items: return
        item = self.ac_items[self.ac_idx]
        line = self.lines[self.cur_ln]
        if item.get("_param_of"):
            seg   = line[:self.cur_col]
            start = max(seg.rfind("("), seg.rfind("'"), seg.rfind('"')) + 1
            end   = self.cur_col
            while end < len(line) and line[end] not in (")", "'", '"', ","):
                end += 1
            insert = item["insert"]
            self.lines[self.cur_ln] = line[:start] + insert + line[end:]
            self.cur_col = start + len(insert)
        else:
            wstart = self._word_start_col()
            insert = item["insert"]
            self.lines[self.cur_ln] = (line[:wstart]
                                       + insert
                                       + line[self.cur_col:])
            self.cur_col = wstart + len(insert)
            if insert.endswith("()") or insert.endswith("('')"):
                self.cur_col -= 1
        self.ac_visible = False; self.ac_items = []

    # ── Render principal ─────────────────────────────
    def draw(self, surface: pygame.Surface):
        self._init_fonts()
        fc   = self.font_code
        fui  = self.font_ui
        fsm  = self.font_sm
        r    = self.rect
        blink = (pygame.time.get_ticks() % 900) < 520

        # Detectar si el script termino
        p = self.penguin
        if (self.running
                and p._script_thread
                and not p._script_thread.is_alive()):
            self.running = False

        pygame.draw.rect(surface, IDE_BG, r)
        pygame.draw.rect(surface, IDE_BORDER, r, 2)

        # ── Titulo ──────────────────────────────────
        tr = self._r_title
        pygame.draw.rect(surface, IDE_TITLE, tr)
        t_s = fui.render(f"  {p.nombre}   —   Python", True, CUI_WHITE)
        surface.blit(t_s, (tr.x + 8,
                            tr.y + (self.TITLE_H - t_s.get_height()) // 2))
        xr = pygame.Rect(tr.right - 27, tr.y + 4, 22, self.TITLE_H - 8)
        pygame.draw.rect(surface, (165, 45, 45), xr)
        surface.blit(fui.render("X", True, CUI_WHITE),
                     fui.render("X", True, CUI_WHITE).get_rect(center=xr.center))

        # ── Toolbar ─────────────────────────────────
        tbr = self._r_toolbar
        pygame.draw.rect(surface, IDE_DARK, tbr)
        pygame.draw.line(surface, IDE_SEP, tbr.bottomleft, tbr.bottomright)

        def btn(label, x, w, bg, fg=CUI_WHITE):
            br = pygame.Rect(x, tbr.y + 4, w, tbr.h - 8)
            pygame.draw.rect(surface, bg, br)
            pygame.draw.rect(surface, IDE_BORDER, br, 1)
            s = fui.render(label, True, fg)
            surface.blit(s, s.get_rect(center=br.center))

        bx = r.x + 8
        run_bg = (80, 40, 40) if self.running else (42, 98, 52)
        btn("▶  Ejecutar  (F5)",  bx,       126, run_bg)
        bx += 134
        stop_bg = (140, 40, 40) if self.running else (60, 50, 50)
        btn("■  Stop  (F6)",      bx,        90, stop_bg,
            (255, 100, 100) if self.running else (100, 80, 80))
        bx += 98
        btn("Limpiar",             bx,        72, (48, 48, 82))

        # Indicador RUNNING
        if self.running:
            t_ms   = pygame.time.get_ticks()
            dots   = "." * ((t_ms // 400) % 4)
            run_s  = fsm.render(f"  RUNNING{dots}", True, (80, 220, 100))
            surface.blit(run_s, (r.x + 360, tbr.y + 9))

        # ── Editor ──────────────────────────────────
        er = self._r_editor
        pygame.draw.rect(surface, IDE_BG, er)
        pygame.draw.rect(surface, IDE_LNBG, (er.x, er.y, _LNPAD, er.h))
        pygame.draw.line(surface, IDE_SEP,
                         (er.x + _LNPAD, er.y),
                         (er.x + _LNPAD, er.bottom))

        for vi in range(self.EDITOR_LINES):
            li = self.scroll + vi
            if li >= len(self.lines): break
            ly = er.y + _EPAD + vi * _LINE_H
            if li == self.cur_ln:
                pygame.draw.rect(surface, IDE_HL,
                                 (er.x + _LNPAD + 1, ly - 1,
                                  self.W - _LNPAD - 2, _LINE_H + 1))
            ln_s = fsm.render(str(li + 1), True, (88, 94, 132))
            surface.blit(ln_s,
                         ln_s.get_rect(right=er.x + _LNPAD - 4, top=ly + 1))
            tx = er.x + _LNPAD + _EPAD
            for text, color in tokenize(self.lines[li]):
                s = fc.render(text, True, color)
                surface.blit(s, (tx, ly))
                tx += fc.size(text)[0]
            if li == self.cur_ln and blink:
                bw = fc.size(self.lines[li][:self.cur_col])[0]
                cx = er.x + _LNPAD + _EPAD + bw
                pygame.draw.line(surface, IDE_CURSOR,
                                 (cx, ly), (cx, ly + _LINE_H - 2), 2)

        # ── Output ──────────────────────────────────
        sep_y = er.bottom
        pygame.draw.line(surface, IDE_SEP, (r.x, sep_y), (r.right, sep_y), self.SEP_H)
        oh_y = sep_y + self.SEP_H
        pygame.draw.rect(surface, IDE_DARK, (r.x, oh_y, self.W, self.OUT_HDR_H))
        surface.blit(fsm.render("  Output", True, (108, 112, 158)),
                     (r.x + 6, oh_y + 3))

        outr = self._r_output
        pygame.draw.rect(surface, IDE_OUT, outr)
        if self.out:
            oy = outr.y + 4
            for text, kind in self.out[-self.OUT_LINES:]:
                col_s = SYN_OK if kind == "ok" else SYN_ERR
                surface.blit(fc.render(text, True, col_s),
                             (outr.x + 8, oy))
                oy += _LINE_H
        else:
            surface.blit(
                fsm.render("(sin output — F5 ejecutar)",
                            True, (62, 68, 105)),
                (outr.x + 8, outr.y + 6))

        # ── Status bar ──────────────────────────────
        str_r = self._r_status
        pygame.draw.rect(surface, IDE_DARK, str_r)
        pygame.draw.line(surface, IDE_SEP, str_r.topleft, str_r.topright)
        st_txt = (f"  RUNNING — F6 para detener"
                  if self.running else
                  f"  Ln {self.cur_ln+1}  Col {self.cur_col+1}"
                  f"   |  {len(self.lines)} lineas")
        st_col = (80, 220, 100) if self.running else (88, 94, 132)
        surface.blit(fsm.render(st_txt, True, st_col),
                     (str_r.x + 4, str_r.y + 3))

        # ── Dropdown AC ─────────────────────────────
        if self.ac_visible and self.ac_items:
            self._draw_ac(surface)

    # ── Render del dropdown AC ───────────────────────
    def _draw_ac(self, surface: pygame.Surface):
        self._init_fonts()
        fc  = self.font_ac
        fsm = self.font_sm
        er  = self._r_editor

        vi    = self.cur_ln - self.scroll
        cur_x = (er.x + _LNPAD + _EPAD
                 + self.font_code.size(
                     self.lines[self.cur_ln][:self._word_start_col()])[0])
        cur_y = er.y + _EPAD + vi * _LINE_H + _LINE_H

        n_vis  = min(len(self.ac_items), AC_MAX_VIS)
        drop_h = n_vis * AC_ITEM_H + 4
        drop_x = min(cur_x, self.rect.right - AC_DROP_W - AC_DOC_W - 4)
        drop_x = max(drop_x, self.rect.x)
        drop_y = cur_y
        if drop_y + drop_h > self.rect.bottom:
            drop_y = cur_y - _LINE_H - drop_h

        drop_rect = pygame.Rect(drop_x, drop_y, AC_DROP_W, drop_h)
        pygame.draw.rect(surface, AC_BG, drop_rect)
        pygame.draw.rect(surface, AC_BORDER, drop_rect, 1)

        selected_item = None
        for vi_i in range(n_vis):
            idx  = self.ac_scroll + vi_i
            if idx >= len(self.ac_items): break
            item = self.ac_items[idx]
            iy   = drop_y + 2 + vi_i * AC_ITEM_H
            item_rect = pygame.Rect(drop_x + 1, iy, AC_DROP_W - 2, AC_ITEM_H)
            if idx == self.ac_idx:
                pygame.draw.rect(surface, AC_SEL_BG, item_rect)
                selected_item = item
            kind_col, kind_ch = AC_KIND_STYLE.get(item["kind"], ((128,128,128), "?"))
            badge = pygame.Rect(drop_x + 3, iy + 3, 14, 14)
            pygame.draw.rect(surface,
                             tuple(max(0, c - 40) for c in kind_col), badge)
            pygame.draw.rect(surface, kind_col, badge, 1)
            surface.blit(fsm.render(kind_ch, True, kind_col),
                         fsm.render(kind_ch, True, kind_col).get_rect(center=badge.center))
            word  = self._word_before_cursor().lower()
            label = item["label"]
            lx    = drop_x + 22
            ly    = iy + (AC_ITEM_H - fc.get_height()) // 2
            if label.lower().startswith(word) and word:
                ms = fc.render(label[:len(word)], True, (240, 244, 255))
                rs = fc.render(label[len(word):], True, (148, 155, 185))
                surface.blit(ms, (lx, ly))
                surface.blit(rs, (lx + ms.get_width(), ly))
            else:
                surface.blit(fc.render(label, True, (200, 205, 230)), (lx, ly))

        # Scrollbar
        if len(self.ac_items) > AC_MAX_VIS:
            ratio = n_vis / len(self.ac_items)
            sb_h  = max(14, int(drop_h * ratio))
            sb_y  = drop_y + int((self.ac_scroll / len(self.ac_items)) * drop_h)
            pygame.draw.rect(surface, (60,65,100),
                             (drop_rect.right - 5, drop_y, 4, drop_h))
            pygame.draw.rect(surface, (110,118,180),
                             (drop_rect.right - 5, sb_y, 4, sb_h))

        # Panel descripcion
        if selected_item:
            doc_lines = selected_item["doc"].split("\n")
            doc_h     = max(64, len(doc_lines) * 15 + 32)
            doc_rect  = pygame.Rect(drop_rect.right + 2, drop_y, AC_DOC_W, doc_h)
            if doc_rect.right > self.rect.right:
                doc_rect.x = drop_rect.x - AC_DOC_W - 2
            if doc_rect.bottom > self.rect.bottom:
                doc_rect.y = self.rect.bottom - doc_h
            pygame.draw.rect(surface, AC_DOC_BG, doc_rect)
            pygame.draw.rect(surface, AC_BORDER, doc_rect, 1)
            surface.blit(fc.render(selected_item["detail"][:36],
                                    True, (180, 200, 255)),
                         (doc_rect.x + 6, doc_rect.y + 5))
            pygame.draw.line(surface, (50, 56, 88),
                             (doc_rect.x + 4, doc_rect.y + 21),
                             (doc_rect.right - 4, doc_rect.y + 21))
            dy = doc_rect.y + 26
            for dl in doc_lines:
                if dy + 13 > doc_rect.bottom - 3: break
                surface.blit(fsm.render(dl, True, (140, 148, 180)),
                             (doc_rect.x + 6, dy))
                dy += 15

        surface.blit(
            fsm.render("Tab/Enter aceptar  ↑↓ navegar  Esc cerrar",
                        True, (60, 66, 100)),
            (drop_rect.x, drop_rect.bottom + 2))