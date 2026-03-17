# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — ui/terminal.py
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

    "tutorial_bash.txt": [
        "╔══════════════════════════════════════════════╗",
        "║      CYBORG-OS  —  Tutorial de Bash          ║",
        "╠══════════════════════════════════════════════╣",
        "║  COMANDOS BASICOS:                           ║",
        "║   pwd          muestra directorio actual     ║",
        "║   ls           lista archivos del directorio ║",
        "║   cat <file>   muestra contenido del archivo ║",
        "║   cd <dir>     cambia de directorio          ║",
        "║   cd ..        sube un directorio            ║",
        "║   clear        limpia la pantalla            ║",
        "║   help         muestra esta ayuda            ║",
        "║                                              ║",
        "║  EJEMPLO:                                    ║",
        "║   $ ls                                       ║",
        "║   $ cat pescar.vim                           ║",
        "║                                              ║",
        "║  Los archivos se desbloquean al avanzar.     ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "pescar.vim": [
        "╔══════════════════════════════════════════════╗",
        "║   pescar.vim  —  Tutorial: Como pescar       ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  El pinguino puede ir a pescar usando:       ║",
        "║                                              ║",
        "║      pescar()                                ║",
        "║                                              ║",
        "║  El pinguino navega AUTOMATICAMENTE a la     ║",
        "║  costa mas cercana y pesca.                  ║",
        "║                                              ║",
        "║  Hay un 40% de probabilidad de exito.        ║",
        "║  Si falla, igual hace el viaje.              ║",
        "║                                              ║",
        "║  La mochila del pinguino aguanta max 5 peces.║",
        "║                                              ║",
        "║  Abre la ventana del pinguino (clic encima)  ║",
        "║  y ejecuta:                                  ║",
        "║      pescar()                                ║",
        "║                                              ║",
        "║  [Pesca 1 pez para desbloquear mas archivos] ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "while_loops.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   while_loops.txt  —  Bucles infinitos       ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Puedes usar while True para automatizar:    ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║                                              ║",
        "║  El pinguino pescara sin parar!              ║",
        "║  Usa el boton STOP (F6) para detenerlo.      ║",
        "║                                              ║",
        "║  Tambien puedes usar for para un numero      ║",
        "║  fijo de repeticiones:                       ║",
        "║                                              ║",
        "║      for i in range(5):                      ║",
        "║          pescar()                            ║",
        "║                                              ║",
        "║  [Pesca 5 peces en total para continuar]     ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "almacenar.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   almacenar.txt  —  Guardar recursos         ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  La mochila del pinguino tiene max 5 peces.  ║",
        "║  Cuando se llene, debes almacenarlos:        ║",
        "║                                              ║",
        "║      almacenar('Pez')                        ║",
        "║                                              ║",
        "║  El pinguino lleva los peces al almacen      ║",
        "║  central y los deposita todos de una vez.    ║",
        "║                                              ║",
        "║  Patron recomendado:                         ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          pescar()                            ║",
        "║          if inventario_lleno('Pez'):         ║",
        "║              almacenar('Pez')                ║",
        "║                                              ║",
        "║  El almacen guarda hasta 500 de cada recurso.║",
        "║                                              ║",
        "║  [Almacena 100 peces para continuar]         ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "talar.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   talar.txt  —  Cortar arboles               ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  En la zona del Bosque (derecha del mapa)    ║",
        "║  hay arboles que puedes talar:               ║",
        "║                                              ║",
        "║      talar()                                 ║",
        "║                                              ║",
        "║  El pinguino va al arbol mas cercano         ║",
        "║  y lo corta. El arbol REGENERA en 20s.       ║",
        "║                                              ║",
        "║  Para optimizar:                             ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          talar()                             ║",
        "║          if inventario_lleno('Madera'):      ║",
        "║              almacenar('Madera')             ║",
        "║                                              ║",
        "║  [Consigue 150 peces y 150 madera almacenados║",
        "║   para desbloquear el siguiente tutorial]    ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "picar_hielo.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   picar_hielo.txt  —  Extraer hielo          ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  En la Mina de Hielo (izquierda del mapa)    ║",
        "║  puedes extraer bloques de hielo:            ║",
        "║                                              ║",
        "║      picar_hielo()                           ║",
        "║                                              ║",
        "║  El hielo es necesario para construir nidos. ║",
        "║                                              ║",
        "║  Script completo de recoleccion:             ║",
        "║                                              ║",
        "║      while True:                             ║",
        "║          picar_hielo()                       ║",
        "║          if inventario_lleno('Hielo'):       ║",
        "║              almacenar('Hielo')              ║",
        "║                                              ║",
        "║  [Consigue en el almacen:                    ║",
        "║   200 peces + 200 madera + 100 hielo         ║",
        "║   para desbloquear el ultimo tutorial]       ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "construir_nido.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   construir_nido.txt  —  Nido Cyborg         ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Ya tienes suficientes recursos!             ║",
        "║  Puedes construir un nido cyborg:            ║",
        "║                                              ║",
        "║      construir_nido()                        ║",
        "║                                              ║",
        "║  COSTO:  50 Madera + 100 Hielo               ║",
        "║  (del almacen global)                        ║",
        "║                                              ║",
        "║  El pinguino navega a la zona FABRICA        ║",
        "║  (arriba a la derecha) y construye el nido.  ║",
        "║                                              ║",
        "║  Una vez construido el nido, podras crear    ║",
        "║  nuevos pinguinos.                           ║",
        "║                                              ║",
        "║  Ver: cat crear_pinguino.txt                 ║",
        "╚══════════════════════════════════════════════╝",
    ],

    "crear_pinguino.txt": [
        "╔══════════════════════════════════════════════╗",
        "║   crear_pinguino.txt  —  Nueva vida cyborg   ║",
        "╠══════════════════════════════════════════════╣",
        "║                                              ║",
        "║  Despues de construir un nido, puedes        ║",
        "║  crear nuevos pinguinos cyborg:              ║",
        "║                                              ║",
        "║      crear_pinguino()                        ║",
        "║                                              ║",
        "║  El nuevo pinguino aparece en la zona        ║",
        "║  de PESCA lista para recibir ordenes.        ║",
        "║                                              ║",
        "║  Clic en el nuevo pinguino para abrir        ║",
        "║  su ventana de comandos individual.          ║",
        "║                                              ║",
        "║  ATENCION: Cada pinguino consume mas hambre! ║",
        "║  Asegurate de tener peces suficientes.       ║",
        "║                                              ║",
        "║  CONSEJO: Asigna tareas distintas a cada     ║",
        "║  pinguino para maximizar la produccion.      ║",
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

    PROMPT = "pingu@cyborg-os:~$ "

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
        self.inp    = ""
        self._history: list[str] = []

        # Inicializar con pantalla de bienvenida
        self._boot_screen()

    # ── Sistema de archivos ──────────────────────────
    def unlock_file(self, filename: str):
        """Desbloquea un archivo en el directorio home."""
        if filename not in self._unlocked_files:
            self._unlocked_files.add(filename)
            if self.estado == "bash":
                self._print(f"[+] Nuevo archivo desbloqueado: {filename}", "cyan")
                self._print(f"    Usa: cat {filename}", "gray")

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
        self._print("║   CYBORG-OS v1.0  — OFFLINE  ║", "cyan")
        self._print("╚══════════════════════════════╝", "cyan")
        self._print("Sistema danado. Reparar? [y/n]:", "white")

    # ── Helpers de output ────────────────────────────
    def _print(self, text: str, color: str = "green"):
        self.output.append((text, color))

    def _prompt_line(self) -> str:
        return self.PROMPT

    # ── Manejo de eventos ────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if not self.show:
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
            self._print("Bienvenido a CYBORG-OS Bash 5.1", "cyan")
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
            self._print("CYBORG-OS 5.1 cyborg-penguin", "green")
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
            "║   CYBORG-OS  —  Comandos disponibles     ║",
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

        rect = pygame.Rect(30, 50, 510, 460)

        # Fondo semitransparente
        bg = pygame.Surface((rect.w, rect.h))
        bg.fill((10, 12, 22))
        bg.set_alpha(252)
        surface.blit(bg, rect.topleft)
        pygame.draw.rect(surface, CUI_CYAN, rect, 2)

        # Titulo
        title_r = pygame.Rect(rect.x, rect.y, rect.w, 20)
        pygame.draw.rect(surface, (20, 25, 45), title_r)
        title_s = font.render("  CYBORG-OS  Terminal  [ESC cerrar]",
                              True, CUI_CYAN)
        surface.blit(title_s, (rect.x + 6, rect.y + 3))
        pygame.draw.line(surface, CUI_CYAN,
                         (rect.x, rect.y + 20),
                         (rect.right, rect.y + 20))

        # Output (scrollado, las ultimas N lineas)
        COLOR_MAP = {
            "green": CUI_GREEN,
            "cyan":  CUI_CYAN,
            "white": (210, 215, 235),
            "gray":  (110, 115, 140),
            "red":   (220, 80, 80),
        }
        content_y   = rect.y + 24
        input_area  = 26
        avail_h     = rect.h - 24 - input_area
        line_h      = 15
        max_lines   = avail_h // line_h

        visible = self.output[-max_lines:] if len(self.output) > max_lines else self.output
        y = content_y
        for text, ckey in visible:
            col = COLOR_MAP.get(ckey, CUI_GREEN)
            s   = font.render(text, True, col)
            surface.blit(s, (rect.x + 8, y))
            y += line_h

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