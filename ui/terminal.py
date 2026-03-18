# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — ui/terminal.py
#  Terminal bash simulada con sistema de archivos virtual
#  y tutoriales que se desbloquean progresivamente.
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import pygame
from config import IDE_DARK, IDE_BG, IDE_BORDER, CUI_CYAN, CUI_GREEN, CUI_GRAY, CUI_WHITE


# ═══════════════════════════════════════════════════════
#  CONTENIDO DE LOS ARCHIVOS VIRTUALES
# ═══════════════════════════════════════════════════════
FILE_CONTENTS: dict[str, list[str]] = {

    # ── OBJETIVO 1: PC reparada ──────────────────────────
    "tutorial_bash.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  SISTEMA RESTAURADO     ║",
        "║   Estado: REPARADO  |  Bateria: 43%          ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Conexion establecida, Pingu-01.             ║",
        "║  La red esta activa. Podes empezar.          ║",
        "║                                              ║",
        "║  Tu primer objetivo es simple:               ║",
        "║  conseguir comida.                           ║",
        "║                                              ║",
        "║  Sin peces no hay energia.                   ║",
        "║  Sin energia no hay colonia.                 ║",
        "║                                              ║",
        "║  Escribi esto en tu editor:                  ║",
        "║                                              ║",
        "║      pescar()                                ║",
        "║                                              ║",
        "║  Clic sobre vos mismo → editor → F5          ║",
        "║                                              ║",
        "║  COMANDOS DE ESTA TERMINAL:                  ║",
        "║   ls      lista archivos disponibles         ║",
        "║   cat X   muestra el contenido de X          ║",
        "║   clear   limpia la pantalla                 ║",
        "║                                              ║",
        "║  OBJETIVO → Pescar 1 pez                     ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "pescar.vim": [
        "╔══════════════════════════════════════════════╗",
        "║   pescar.vim  —  Referencia rapida           ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║   pescar()         ir a pescar               ║",
        "║   talar()          cortar un arbol           ║",
        "║   picar_hielo()    extraer hielo             ║",
        "║   almacenar('X')   depositar en almacen      ║",
        "║   construir_nido(col, fila)  construir iglu  ║",
        "║   crear_pinguino() nuevo pinguino cyborg     ║",
        "║                                              ║",
        "║  El pinguino navega SOLO al destino.         ║",
        "║  Exito de pesca: 40%. Mochila max: 5 items.  ║",
        "║                                              ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 2: primer pez ───────────────────────────
    "while_loops.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Registro: 1 pez        ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Bien. Funciona.                             ║",
        "║  Ahora aprende a no parar.                   ║",
        "║                                              ║",
        "║  Existe una instruccion que repite todo      ║",
        "║  indefinidamente. Se llama 'while True':     ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║                                              ║",
        "║  Esto no se detiene solo.                    ║",
        "║  Usa F6 para frenar el script.               ║",
        "║                                              ║",
        "║  OBJETIVO → Conseguir 5 peces                ║",
        "║              para habilitar el Almacen       ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 3: 5 peces ──────────────────────────────
    "almacenar.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Almacen Central ON     ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  El almacen esta operativo.                  ║",
        "║  Un recurso en tu mochila no sirve de nada   ║",
        "║  si no pasa por el almacen central.          ║",
        "║                                              ║",
        "║  Aprende a almacenar:                        ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║          almacenar('Pez')                    ║",
        "║                                              ║",
        "║  El almacen guarda hasta 500 por recurso.    ║",
        "║                                              ║",
        "║  OBJETIVO → Almacenar 35 peces               ║",
        "║              para habilitar el Bosque        ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 4: 100 peces ────────────────────────────
    "talar.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Bosque Glacial ON      ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Los arboles de cristal llevan anos          ║",
        "║  sin ser talados. Necesitas madera           ║",
        "║  para construir. Sin construccion,           ║",
        "║  no hay expansion.                           ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          talar()                             ║",
        "║          almacenar('Madera')                 ║",
        "║                                              ║",
        "║  Podes combinar con la pesca:                ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║          almacenar('Pez')                    ║",
        "║          talar()                             ║",
        "║          almacenar('Madera')                 ║",
        "║                                              ║",
        "║  OBJETIVO → 70 peces + 35 madera             ║",
        "║              para habilitar la Mina          ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 5: 150/150 ──────────────────────────────
    "picar_hielo.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Mina de Hielo ON       ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Bajo la superficie hay mineral puro.        ║",
        "║  El hielo de aca no es agua —                ║",
        "║  es el material con el que se construyen     ║",
        "║  las estructuras permanentes.                ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║          almacenar('Pez')                    ║",
        "║          talar()                             ║",
        "║          almacenar('Madera')                 ║",
        "║          picar_hielo()                       ║",
        "║          almacenar('Hielo')                  ║",
        "║                                              ║",
        "║  Este script trabaja los tres recursos.      ║",
        "║  Dejalo correr y vuelve cuando tengas        ║",
        "║  suficiente.                                 ║",
        "║                                              ║",
        "║  OBJETIVO → 100 peces / 70 madera / 50       ║",
        "║              hielo para habilitar Iglu       ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 6: 200/200/100 → construir ─────────────
    "construir_nido.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Zona de Construccion   ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Tenes los materiales.                       ║",
        "║  Ahora viene lo importante.                  ║",
        "║                                              ║",
        "║  Un iglu no es solo refugio.                 ║",
        "║  Es infraestructura. Es el nucleo.           ║",
        "║  Sin el, no podes reproducirte.              ║",
        "║                                              ║",
        "║  La zona Iglu es una MATRIZ de 5x4:          ║",
        "║                                              ║",
        "║    col→  0    1    2    3    4               ║",
        "║  fila↓ ┌────┬────┬────┬────┬────┐           ║",
        "║    0   │    │    │    │    │    │           ║",
        "║    1   │    │    │    │    │    │           ║",
        "║    2   │    │    │    │    │    │           ║",
        "║    3   │    │    │    │    │    │           ║",
        "║        └────┴────┴────┴────┴────┘           ║",
        "║                                              ║",
        "║      construir_nido(2, 1)                    ║",
        "║                                              ║",
        "║  COSTO: 50 Madera + 100 Hielo por nido       ║",
        "║                                              ║",
        "║  OBJETIVO → Construir un iglu                ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── OBJETIVO 7: iglu construido ──────────────────────
    "crear_pinguino.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   PENGUIN-OS v0.1  —  Reproduccion Cyborg    ║",
        "║   Bateria: 100%  |  Senal: optima            ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  El iglu esta en pie.                        ║",
        "║  Ahora podes crear vida.                     ║",
        "║                                              ║",
        "║  Cada pinguino nuevo tiene su propio editor. ║",
        "║  Puede correr su propio script.              ║",
        "║  Puede trabajar mientras vos descansas.      ║",
        "║                                              ║",
        "║      crear_pinguino()                        ║",
        "║                                              ║",
        "║  Una colonia de tres ya puede sostenerse     ║",
        "║  sola si cada uno tiene su tarea:            ║",
        "║                                              ║",
        "║   # Pingu-02                                 ║",
        "║   while True:                                ║",
        "║       pescar()                               ║",
        "║       almacenar('Pez')                       ║",
        "║                                              ║",
        "║   # Pingu-03                                 ║",
        "║   while True:                                ║",
        "║       talar()                                ║",
        "║       almacenar('Madera')                    ║",
        "║                                              ║",
        "║  OBJETIVO FINAL → Crear 3 pinguinos          ║",
        "╚══════════════════════════════════════════════╝",
    ],

    # ── FIN: 3 pingüinos creados ─────────────────────────
    "transmision_final.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   TRANSMISION FINAL  —  MISION COMPLETADA    ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Tres pinguinos. Un iglu. Una colonia.       ║",
        "║                                              ║",
        "║  Empezaste con una PC rota y un comando.     ║",
        "║  Ahora tenes una red.                        ║",
        "║                                              ║",
        "║  No hay mas objetivos despues de este.       ║",
        "║  A partir de aca, el codigo es tuyo.         ║",
        "║                                              ║",
        "║  ==========================================  ║",
        "║                                              ║",
        "║   Una colonia que se programa sola           ║",
        "║   es una colonia que sobrevive.              ║",
        "║                                              ║",
        "║  ==========================================  ║",
        "║                                              ║",
        "║              FIN DE TRANSMISION              ║",
        "║                                              ║",
        "╚══════════════════════════════════════════════╝",
    ],
}


# ═══════════════════════════════════════════════════════
#  TERMINAL BASH SIMULADA
# ═══════════════════════════════════════════════════════
class ComputerTerminal:
    """
    Terminal bash simulada con:
    - Sistema de archivos virtual
    - Comandos: ls, cat, pwd, cd, cd .., clear, help
    - Archivos que se desbloquean progresivamente
    - Fase inicial de reparacion (y/n)
    """

    PROMPT = "pingu@penguin-os:~$ "

    def __init__(self, row: int, col: int):
        self.row    = row
        self.col    = col
        self.show   = False

        # Estado de la maquina
        self.estado = "offline"   # offline | reparando | bash

        # Sistema de archivos virtual
        # Directorio actual y estructura
        self._cwd   = "/home/pingu"
        self._fs: dict[str, dict] = {
            "/home/pingu": {},           # archivos desbloqueados aqui
            "/home/pingu/docs": {},      # subdirectorio futuro
        }
        self._unlocked_files: set[str] = set()

        # Output y entrada
        self.output: list[tuple[str, str]] = []  # (texto, color_key)
        self.inp     = ""
        self._history: list[str] = []
        self._scroll    = 0     # 0 = ver el fondo, positivo = scrolleado hacia arriba
        self.has_unread = False # True mientras haya objetivos sin leer

        # Posicion y drag
        # Centrado en pantalla — importamos config para obtener dimensiones
        from config import WIN_W, WIN_H
        _tw, _th = 510, 460
        _tx = (WIN_W - _tw) // 2
        _ty = (WIN_H - _th) // 2
        self.rect   = pygame.Rect(_tx, _ty, _tw, _th)
        self._drag  = False
        self._dox   = 0
        self._doy   = 0

        # Inicializar con pantalla de bienvenida
        self._boot_screen()

    # ── Sistema de archivos ──────────────────────────
    def unlock_file(self, filename: str):
        """Desbloquea un archivo y muestra su contenido automáticamente."""
        if filename not in self._unlocked_files:
            self._unlocked_files.add(filename)
            self.has_unread = True
            if self.estado == "bash":
                self._print("", "green")
                self._print(f"[+] Nuevo archivo desbloqueado: {filename}", "orange")
                self._print("─" * 48, "gray")
                content = FILE_CONTENTS.get(filename, [])
                for line in content:
                    self._print(line, "green")
                self._print("", "green")

    def on_open(self):
        """Llamar cuando el jugador abre la terminal."""
        if self.has_unread and self.estado == "bash":
            self._print("", "green")
            self._print("╔══════════════════════════════════════╗", "cyan")
            self._print("║  ! TENES NUEVOS OBJETIVOS ARRIBA  !  ║", "cyan")
            self._print("║     Scrollea hacia arriba para verlos ║", "gray")
            self._print("╚══════════════════════════════════════╝", "cyan")
            self._print("", "green")
        self.has_unread = False

    def draw_world_indicator(self, surface, cam_col, cam_row,
                              font, tile_size, vw, vh, hud_h):
        """Dibuja un '!' parpadeante sobre el tile de la PC en el mundo."""
        if not self.has_unread:
            return
        vc = self.col - cam_col
        vr = self.row - cam_row
        if not (0 <= vc < vw and 0 <= vr < vh):
            return
        if (pygame.time.get_ticks() // 350) % 2 == 0:
            cx  = vc * tile_size + tile_size // 2
            cy  = vr * tile_size + hud_h
            bw, bh = 18, 18
            bx  = cx - bw // 2
            by  = cy - bh - 2
            pygame.draw.rect(surface, (200, 100, 0),
                             (bx, by, bw, bh), border_radius=4)
            pygame.draw.rect(surface, (255, 200, 0),
                             (bx, by, bw, bh), 1, border_radius=4)
            s = font.render("!", True, (255, 255, 255))
            surface.blit(s, s.get_rect(center=(cx, by + bh // 2)))

    def _list_files(self, path: str | None = None) -> list[str]:
        """Lista los archivos del directorio actual."""
        d = path or self._cwd
        if d == "/home/pingu":
            return sorted(self._unlocked_files)
        return []

    def _read_file(self, filename: str) -> list[str] | None:
        """Devuelve el contenido de un archivo o None si no existe."""
        if filename in self._unlocked_files and filename in FILE_CONTENTS:
            return FILE_CONTENTS[filename]
        return None

    # ── Boot y repair ────────────────────────────────
    def _boot_screen(self):
        self.output = []
        self._print("╔══════════════════════════════╗", "cyan")
        self._print("║   PENGUIN-OS v1.0  — OFFLINE  ║", "cyan")
        self._print("╚══════════════════════════════╝", "cyan")
        self._print("Sistema danado. Reparar? [y/n]:", "white")

    # ── Helpers de output ────────────────────────────
    def _print(self, text: str, color: str = "green"):
        self.output.append((text, color))
        self._scroll = 0   # auto-scroll al fondo cuando hay output nuevo

    def _prompt_line(self) -> str:
        return self.PROMPT

    # ── Manejo de eventos ────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if not self.show:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            title_r = pygame.Rect(self.rect.x, self.rect.y,
                                  self.rect.w, 20)
            if title_r.collidepoint(mx, my):
                self._drag = True
                self._dox  = mx - self.rect.x
                self._doy  = my - self.rect.y
                return

        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag = False

        elif event.type == pygame.MOUSEMOTION:
            if self._drag:
                mx, my = event.pos
                from config import WIN_W, WIN_H
                self.rect.x = max(0, min(mx - self._dox,
                                         WIN_W - self.rect.w))
                self.rect.y = max(0, min(my - self._doy,
                                         WIN_H - self.rect.h))
                return

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                input_area = 26
                line_h     = 15
                avail_h    = self.rect.h - 24 - input_area
                max_lines  = avail_h // line_h
                max_scroll = max(0, len(self.output) - max_lines)
                self._scroll = max(0, min(self._scroll + event.y, max_scroll))
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show = False
            elif event.key == pygame.K_RETURN:
                cmd = self.inp.strip()
                self._print(self._prompt_line() + cmd, "white")
                if cmd:
                    self._history.append(cmd)
                self._dispatch(cmd)
                self.inp = ""
            elif event.key == pygame.K_BACKSPACE:
                self.inp = self.inp[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.inp += event.unicode

    def _dispatch(self, cmd: str):
        """Enruta el comando al handler correcto segun el estado."""
        if self.estado == "offline":
            self._handle_offline(cmd)
        elif self.estado == "reparando":
            self._handle_reparando(cmd)
        elif self.estado == "bash":
            self._handle_bash(cmd)

    # ── Estado: offline ──────────────────────────────
    def _handle_offline(self, cmd: str):
        c = cmd.lower()
        if c == "y":
            self._print("Iniciando secuencia de reparacion...", "green")
            self._print("[ OK ] Cargando kernel cyborg...", "green")
            self._print("[ OK ] Montando sistema de archivos...", "green")
            self._print("[ OK ] Inicializando red neuronal...", "green")
            self._print("Sistema reparado! Escribe 'bash' para iniciar shell.", "cyan")
            self.estado = "reparando"
        elif c == "n":
            self._print("Operacion cancelada.", "gray")
        else:
            self._print("Responde 'y' para reparar o 'n' para cancelar.", "gray")

    # ── Estado: reparando (pre-bash) ─────────────────
    def _handle_reparando(self, cmd: str):
        if cmd.lower() == "bash":
            self.estado = "bash"
            self._print("", "green")
            self._print("Bienvenido a PENGUIN-OS Bash 5.1", "cyan")
            self._print("Escribe 'help' para ver los comandos.", "gray")
            self._print("Escribe 'ls' para ver los archivos disponibles.", "gray")
            self._print("", "green")
        else:
            self._print(f"Comando no reconocido. Escribe 'bash' para iniciar.", "gray")

    # ── Estado: bash ─────────────────────────────────
    def _handle_bash(self, raw: str):
        if not raw:
            return
        parts = raw.split()
        cmd   = parts[0].lower()
        args  = parts[1:] if len(parts) > 1 else []

        if cmd == "ls":
            self._cmd_ls(args)
        elif cmd == "cat":
            self._cmd_cat(args)
        elif cmd == "pwd":
            self._print(self._cwd, "green")
        elif cmd == "cd":
            self._cmd_cd(args)
        elif cmd in ("clear", "cls"):
            self.output = []
        elif cmd == "help":
            self._cmd_help()
        elif cmd == "echo":
            self._print(" ".join(args), "green")
        elif cmd == "whoami":
            self._print("pingu", "green")
        elif cmd == "uname":
            self._print("PENGUIN-OS 5.1 penguin-was-replace", "green")
        elif cmd == "exit":
            self.show = False
        else:
            self._print(f"bash: {cmd}: comando no encontrado", "gray")
            self._print("Escribe 'help' para ver los comandos disponibles.", "gray")

    def _cmd_ls(self, args: list[str]):
        files = self._list_files()
        if not files:
            self._print("(directorio vacio — aun no hay archivos desbloqueados)", "gray")
            self._print("Repara la PC primero y avanza en el juego.", "gray")
            return
        # Mostrar en columnas
        self._print("total " + str(len(files)), "gray")
        for f in files:
            ext  = f.rsplit(".", 1)[-1] if "." in f else ""
            icon = {"txt": "📄", "vim": "📝", "sh": "⚙"}.get(ext, "📄")
            self._print(f"  {icon}  {f}", "green")

    def _cmd_cat(self, args: list[str]):
        if not args:
            self._print("uso: cat <archivo>", "gray")
            return
        fname = args[0]
        # Quitar ./ al inicio si lo pusieron
        fname = fname.lstrip("./")
        content = self._read_file(fname)
        if content is None:
            if fname in FILE_CONTENTS:
                self._print(f"cat: {fname}: archivo bloqueado (sigue avanzando!)", "gray")
            else:
                self._print(f"cat: {fname}: No existe el archivo", "gray")
            return
        for line in content:
            self._print(line, "green")

    def _cmd_cd(self, args: list[str]):
        if not args or args[0] == "~":
            self._cwd = "/home/pingu"
            return
        target = args[0]
        if target == "..":
            if self._cwd != "/":
                parts = self._cwd.rsplit("/", 1)
                self._cwd = parts[0] if parts[0] else "/"
        elif target == "docs":
            self._cwd = "/home/pingu/docs"
            self._print("(directorio vacio)", "gray")
        else:
            self._print(f"cd: {target}: No existe el directorio", "gray")

    def _cmd_help(self):
        lines = [
            "╔══════════════════════════════════════════╗",
            "║   PENGUIN-OS  —  Comandos disponibles     ║",
            "╠══════════════════════════════════════════╣",
            "║   ls           lista archivos            ║",
            "║   cat <file>   muestra contenido         ║",
            "║   pwd          directorio actual         ║",
            "║   cd <dir>     cambiar directorio        ║",
            "║   cd ..        subir un nivel            ║",
            "║   clear        limpiar pantalla          ║",
            "║   echo <text>  imprimir texto            ║",
            "║   whoami       usuario actual            ║",
            "║   uname        info del sistema          ║",
            "║   exit         cerrar terminal           ║",
            "╚══════════════════════════════════════════╝",
        ]
        for l in lines:
            self._print(l, "green")

    # ── Render ───────────────────────────────────────
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if not self.show:
            return

        rect = self.rect

        # Fondo semitransparente
        bg = pygame.Surface((rect.w, rect.h))
        bg.fill((10, 12, 22))
        bg.set_alpha(252)
        surface.blit(bg, rect.topleft)
        pygame.draw.rect(surface, CUI_CYAN, rect, 2)

        # Titulo
        title_r = pygame.Rect(rect.x, rect.y, rect.w, 20)
        pygame.draw.rect(surface, (20, 25, 45), title_r)
        title_s = font.render("  PENGUIN-OS  Terminal  [ESC cerrar]",
                              True, CUI_CYAN)
        surface.blit(title_s, (rect.x + 6, rect.y + 3))
        pygame.draw.line(surface, CUI_CYAN,
                         (rect.x, rect.y + 20),
                         (rect.right, rect.y + 20))

        # Output con scroll
        COLOR_MAP = {
            "green":  CUI_GREEN,
            "cyan":   CUI_CYAN,
            "white":  (210, 215, 235),
            "gray":   (110, 115, 140),
            "red":    (220, 80, 80),
            "orange": (255, 160, 0),
        }
        SB_W        = 8               # ancho de la scrollbar
        content_y   = rect.y + 24
        input_area  = 26
        avail_h     = rect.h - 24 - input_area
        line_h      = 15
        max_lines   = avail_h // line_h
        total       = len(self.output)
        max_scroll  = max(0, total - max_lines)
        scroll      = min(self._scroll, max_scroll)

        # índice de inicio: scroll=0 → mostrar últimas líneas; scroll>0 → subir
        start_idx   = max(0, total - max_lines - scroll)
        visible     = self.output[start_idx:start_idx + max_lines]

        y = content_y
        for text, ckey in visible:
            col = COLOR_MAP.get(ckey, CUI_GREEN)
            s   = font.render(text, True, col)
            surface.blit(s, (rect.x + 8, y))
            y += line_h

        # ── Scrollbar vertical ───────────────────────
        if total > max_lines:
            sb_x     = rect.right - SB_W - 2
            sb_y     = content_y
            sb_h     = avail_h
            # track
            pygame.draw.rect(surface, (18, 20, 36),
                             (sb_x, sb_y, SB_W, sb_h))
            # thumb
            ratio    = max_lines / total
            thumb_h  = max(16, int(sb_h * ratio))
            pct      = 1.0 - (scroll / max_scroll) if max_scroll else 1.0
            thumb_y  = sb_y + int(pct * (sb_h - thumb_h))
            pygame.draw.rect(surface, (70, 85, 130),
                             (sb_x + 1, thumb_y, SB_W - 2, thumb_h))
            pygame.draw.rect(surface, (100, 115, 170),
                             (sb_x + 1, thumb_y, SB_W - 2, thumb_h), 1)

        # Linea de input
        sep_y = rect.bottom - input_area
        pygame.draw.line(surface, (40, 50, 70),
                         (rect.x, sep_y), (rect.right, sep_y))

        if self.estado == "bash":
            prompt_txt = self.PROMPT + self.inp + "█"
            prompt_col = CUI_CYAN
        else:
            prompt_txt = "$ " + self.inp + "█"
            prompt_col = (180, 220, 140)

        ps = font.render(prompt_txt, True, prompt_col)
        surface.blit(ps, (rect.x + 8, sep_y + 6))