# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — ui/terminal.py
# ═══════════════════════════════════════════════════════
import pygame
from config import IDE_DARK, CUI_CYAN, CUI_GREEN, CUI_GRAY

TUTORIAL_TXT = """\
 +--------------------------------------------+
 |   tutorial.exe  -  Cyborg Penguins         |
 +--------------------------------------------+
 |  COMANDOS DISPONIBLES:                     |
 |   pescar()           -> navega y pesca     |
 |   talar()            -> navega y tala      |
 |   picar_hielo()      -> navega y extrae    |
 |   almacenar('X')     -> navega y almacena  |
 |      X: 'Pez' | 'Madera' | 'Hielo'         |
 |   crear_pinguino()   -> crea nuevo cyborg  |
 |                                            |
 |  Los pinguinos navegan AUTOMATICAMENTE.    |
 |  Los bucles infinitos funcionan:           |
 |   while True:                              |
 |       pescar()                             |
 |       almacenar('Pez')                     |
 |  Usa el boton STOP para detenerlos.        |
 |                                            |
 |  ESTRUCTURAS:                              |
 |   for i in range(n): ...                   |
 |   while condicion: ...                     |
 |   if / elif / else: ...                    |
 |   def nombre_funcion(): ...                |
 +--------------------------------------------+"""


class ComputerTerminal:
    def __init__(self, row: int, col: int):
        self.row    = row
        self.col    = col
        self.show   = False
        self.estado = "inactiva"
        self.output = [
            "Cyborg OS v1.0  -  OFFLINE",
            "Quieres reparar el sistema ? press: y/n",
        ]
        self.inp = ""

    def handle_event(self, event: pygame.event.Event):
        if not self.show:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show = False
            elif event.key == pygame.K_RETURN:
                self._process(self.inp.strip())
                self.inp = ""
            elif event.key == pygame.K_BACKSPACE:
                self.inp = self.inp[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.inp += event.unicode

    def _process(self, cmd: str):
        self.output.append(f"$ {cmd}")
        c = cmd.lower()
        if c == "y":
            self.output += [
                "Reparando sistema...  [OK]",
                "Archivo detectado: tutorial.exe",
                "Escribe  tutorial.exe  para continuar",
            ]
            self.estado = "reparando"
        elif c == "tutorial.exe":
            self.output += TUTORIAL_TXT.split("\n")
            self.estado = "lista"
        elif c == "n":
            self.output.append("...")
        else:
            self.output.append("Comando no reconocido.")

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if not self.show:
            return
        rect = pygame.Rect(40, 60, 490, 430)
        bg   = pygame.Surface((rect.w, rect.h))
        bg.fill(IDE_DARK)
        bg.set_alpha(248)
        surface.blit(bg, rect.topleft)
        pygame.draw.rect(surface, CUI_CYAN, rect, 2)

        y = rect.y + 8
        for line in self.output[-25:]:
            s = font.render(line, True, CUI_GREEN)
            surface.blit(s, (rect.x + 10, y))
            y += 16

        pygame.draw.line(surface, CUI_GRAY,
                         (rect.x, rect.bottom - 26),
                         (rect.right, rect.bottom - 26))
        inp_s = font.render(f"$ {self.inp}_", True, CUI_CYAN)
        surface.blit(inp_s, (rect.x + 10, rect.bottom - 22))
        hint = font.render("[ESC  cerrar]", True, CUI_GRAY)
        surface.blit(hint,
                     hint.get_rect(right=rect.right - 6, top=rect.y + 4))
