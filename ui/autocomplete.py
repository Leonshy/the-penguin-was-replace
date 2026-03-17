# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — ui/autocomplete.py
# ═══════════════════════════════════════════════════════

AC_DB = [
    # ── Funciones del juego ──────────────────────────
    {
        "label":  "pescar",
        "kind":   "fn",
        "insert": "pescar()",
        "detail": "pescar() -> None",
        "doc":    "Navega a la costa mas cercana\ny pesca 1 pez.\nSe puede usar en bucles infinitos.",
    },
    {
        "label":  "talar",
        "kind":   "fn",
        "insert": "talar()",
        "detail": "talar() -> None",
        "doc":    "Navega al arbol mas cercano\ny lo tala.\nAgrega 'Madera' al inventario.",
    },
    {
        "label":  "picar_hielo",
        "kind":   "fn",
        "insert": "picar_hielo()",
        "detail": "picar_hielo() -> None",
        "doc":    "Navega a la mina mas cercana\ny extrae 1 bloque de hielo.",
    },
    {
        "label":  "almacenar",
        "kind":   "fn",
        "insert": "almacenar('')",
        "detail": "almacenar(material: str) -> None",
        "doc":    "Navega al almacen y deposita\n1 unidad del material.\nValores: 'Pez' | 'Madera' | 'Hielo'",
    },
    {
        "label":  "construir_nido",
        "kind":   "fn",
        "insert": "construir_nido(0, 0)",
        "detail": "construir_nido(col: int, fila: int) -> None",
        "doc":    "Construye un nido en la MATRIZ de la fabrica.\ncol: 0-4  fila: 0-3\nCosto: 50 Madera + 100 Hielo\nEj: construir_nido(2, 1)",
    },
    {
        "label":  "crear_pinguino",
        "kind":   "fn",
        "insert": "crear_pinguino()",
        "detail": "crear_pinguino() -> None",
        "doc":    "Navega a la fabrica y crea\nun nuevo pinguino cyborg.",
    },
    # ── Parametros de almacenar ──────────────────────
    {
        "label":  "'Pez'",
        "kind":   "param",
        "insert": "'Pez'",
        "detail": "almacenar('Pez')",
        "doc":    "Almacena un pez del inventario.",
        "_param_of": "almacenar",
    },
    {
        "label":  "'Madera'",
        "kind":   "param",
        "insert": "'Madera'",
        "detail": "almacenar('Madera')",
        "doc":    "Almacena madera del inventario.",
        "_param_of": "almacenar",
    },
    {
        "label":  "'Hielo'",
        "kind":   "param",
        "insert": "'Hielo'",
        "detail": "almacenar('Hielo')",
        "doc":    "Almacena hielo del inventario.",
        "_param_of": "almacenar",
    },
    # ── Builtins ────────────────────────────────────
    {
        "label":  "print",
        "kind":   "bi",
        "insert": "print()",
        "detail": "print(*args) -> None",
        "doc":    "Imprime en el area de output.",
    },
    {
        "label":  "range",
        "kind":   "bi",
        "insert": "range()",
        "detail": "range(stop) | range(start, stop[, step])",
        "doc":    "Genera una secuencia de enteros.",
    },
    {
        "label":  "len",
        "kind":   "bi",
        "insert": "len()",
        "detail": "len(obj) -> int",
        "doc":    "Devuelve la longitud de un objeto.",
    },
    {
        "label":  "int",
        "kind":   "bi",
        "insert": "int()",
        "detail": "int(x) -> int",
        "doc":    "Convierte a entero.",
    },
    {
        "label":  "str",
        "kind":   "bi",
        "insert": "str()",
        "detail": "str(x) -> str",
        "doc":    "Convierte a cadena.",
    },
    # ── Snippets ────────────────────────────────────
    {
        "label":  "for",
        "kind":   "snip",
        "insert": "for i in range():",
        "detail": "for <var> in <iterable>:",
        "doc":    "Bucle for.\nEjemplo:\n  for i in range(5):\n      pescar()",
    },
    {
        "label":  "while",
        "kind":   "snip",
        "insert": "while :",
        "detail": "while <condicion>:",
        "doc":    "Bucle while.\nwhile True: loop infinito!\n  while True:\n      pescar()",
    },
    {
        "label":  "if",
        "kind":   "snip",
        "insert": "if :",
        "detail": "if <condicion>:",
        "doc":    "Condicional if.",
    },
    {
        "label":  "elif",
        "kind":   "snip",
        "insert": "elif :",
        "detail": "elif <condicion>:",
        "doc":    "Rama elif.",
    },
    {
        "label":  "else",
        "kind":   "snip",
        "insert": "else:",
        "detail": "else:",
        "doc":    "Rama else.",
    },
    {
        "label":  "def",
        "kind":   "snip",
        "insert": "def ():",
        "detail": "def <nombre>(<params>):",
        "doc":    "Define una funcion.\nEjemplo:\n  def cosechar():\n      pescar()\n      almacenar('Pez')",
    },
    # ── Keywords ────────────────────────────────────
    {
        "label":  "return",
        "kind":   "kw",
        "insert": "return ",
        "detail": "return <valor>",
        "doc":    "Devuelve un valor de la funcion.",
    },
    {
        "label":  "True",
        "kind":   "kw",
        "insert": "True",
        "detail": "True",
        "doc":    "Valor booleano verdadero.\nUso: while True: loop infinito.",
    },
    {
        "label":  "False",
        "kind":   "kw",
        "insert": "False",
        "detail": "False",
        "doc":    "Valor booleano falso.",
    },
    {
        "label":  "None",
        "kind":   "kw",
        "insert": "None",
        "detail": "None",
        "doc":    "Valor nulo.",
    },
    {
        "label":  "break",
        "kind":   "kw",
        "insert": "break",
        "detail": "break",
        "doc":    "Sale del bucle actual.",
    },
    {
        "label":  "continue",
        "kind":   "kw",
        "insert": "continue",
        "detail": "continue",
        "doc":    "Salta a la siguiente iteracion.",
    },
    {
        "label":  "pass",
        "kind":   "kw",
        "insert": "pass",
        "detail": "pass",
        "doc":    "Instruccion vacia (placeholder).",
    },
    {
        "label":  "in",
        "kind":   "kw",
        "insert": "in ",
        "detail": "in <iterable>",
        "doc":    "Operador de pertenencia / iteracion.",
    },
    {
        "label":  "not",
        "kind":   "kw",
        "insert": "not ",
        "detail": "not <expr>",
        "doc":    "Negacion logica.",
    },
    {
        "label":  "and",
        "kind":   "kw",
        "insert": "and ",
        "detail": "<a> and <b>",
        "doc":    "AND logico.",
    },
    {
        "label":  "or",
        "kind":   "kw",
        "insert": "or ",
        "detail": "<a> or <b>",
        "doc":    "OR logico.",
    },
]

KEYWORDS = frozenset([
    'for', 'while', 'if', 'elif', 'else', 'def', 'return',
    'in', 'not', 'and', 'or', 'True', 'False', 'None',
    'break', 'continue', 'pass', 'range',
])
GAME_FNS = frozenset([
    'pescar', 'talar', 'picar_hielo', 'almacenar',
    'crear_pinguino', 'construir_nido',
])
BUILTINS = frozenset([
    'print', 'len', 'int', 'str', 'float', 'list', 'bool',
])


def tokenize(line: str) -> list[tuple[str, tuple]]:
    """Divide una linea en tokens (texto, color)."""
    from config import (SYN_CMT, SYN_STR, SYN_NUM,
                        SYN_KW, SYN_FN, SYN_BI, SYN_DEF, SYN_PCT)
    tokens = []
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if ch == '#':
            tokens.append((line[i:], SYN_CMT)); break
        if ch in ('"', "'"):
            j = i + 1
            while j < n and line[j] != ch: j += 1
            j = min(j + 1, n)
            tokens.append((line[i:j], SYN_STR)); i = j; continue
        if ch.isdigit():
            j = i
            while j < n and (line[j].isdigit() or line[j] == '.'): j += 1
            tokens.append((line[i:j], SYN_NUM)); i = j; continue
        if ch.isalpha() or ch == '_':
            j = i
            while j < n and (line[j].isalnum() or line[j] == '_'): j += 1
            word  = line[i:j]
            color = (SYN_KW if word in KEYWORDS else
                     SYN_FN if word in GAME_FNS else
                     SYN_BI if word in BUILTINS else SYN_DEF)
            tokens.append((word, color)); i = j; continue
        tokens.append((ch, SYN_PCT)); i += 1
    return tokens