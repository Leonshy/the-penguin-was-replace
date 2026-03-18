# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — config.py
#  Resolución grande + paleta GBA mejorada
# ═══════════════════════════════════════════════════════

# ── Mundo ───────────────────────────────────────────────
T      = 64          # tile size
WW     = 21          # world width  (tiles)
WH     = 14          # world height (tiles)
VW     = 15          # viewport cols (era 10)
VH     = 10          # viewport rows (era 9)
WIN_W  = VW * T      # 672 px
HUD_H  = 80
BAR_H  = 20
WIN_H  = VH * T + HUD_H + BAR_H
FPS    = 30

# ── Velocidad ───────────────────────────────────────────
MOVE_DELAY   = 3
ACTION_DELAY = 8

# ── Paleta UI ───────────────────────────────────────────
CUI_BG     = (  6,   8,  18)
CUI_WHITE  = (224, 228, 248)
CUI_CYAN   = (  0, 220, 220)
CUI_GREEN  = ( 48, 210,  88)
CUI_GRAY   = (180, 190, 220)
CUI_ORANGE = (255, 168,  40)
CUI_RED    = (224,  56,  56)
CUI_BLACK  = (  0,   0,   0)
CUI_YELLOW = (248, 232,  48)
CUI_PURPLE = (180,  80, 220)
CUI_BLUE   = ( 48, 120, 255)

# ── Colores de tiles ────────────────────────────────────
TILE_COLORS = {
    "f_pesca"    : (  8,  28,  56),
    "f_bosque"   : (  8,  36,  12),
    "f_mina"     : ( 24,  24,  40),
    "f_almacen"  : ( 20,  14,  48),
    "f_fabrica"  : (  8,  36,  44),
    "f_yermo"    : ( 18,  18,  26),
    "agua"       : ( 16,  52, 160),
    "costa"      : (  0, 136, 136),
    "arbol"      : ( 24, 108,  24),
    "mina"       : ( 72,  76, 104),
    "almacen"    : ( 52,  44,  96),
    "fabrica"    : ( 32, 104, 116),
    "computadora": ( 40,  48, 184),
    "nido"       : (112,  72,  32),
}

# ── IDE ─────────────────────────────────────────────────
IDE_BG     = ( 28,  30,  46)
IDE_DARK   = ( 20,  22,  36)
IDE_TITLE  = ( 36,  38,  60)
IDE_HL     = ( 36,  42,  68)
IDE_LNBG   = ( 20,  22,  38)
IDE_BORDER = ( 64,  70, 120)
IDE_CURSOR = (210, 220, 255)
IDE_SEP    = ( 44,  48,  84)
IDE_OUT    = ( 12,  14,  26)

# ── Syntax highlighting ─────────────────────────────────
SYN_KW  = (197, 134, 192)
SYN_BI  = ( 86, 156, 214)
SYN_FN  = (255, 215,  80)
SYN_STR = (206, 145, 120)
SYN_NUM = (181, 206, 168)
SYN_CMT = (106, 153,  85)
SYN_DEF = (220, 220, 222)
SYN_PCT = (180, 186, 202)
SYN_OK  = ( 78, 201, 176)
SYN_ERR = (244,  71,  71)

# ── Autocomplete ────────────────────────────────────────
AC_BG      = ( 30,  32,  50)
AC_BORDER  = ( 64,  70, 120)
AC_SEL_BG  = ( 48,  88, 148)
AC_DOC_BG  = ( 22,  24,  40)
AC_ITEM_H  = 22
AC_MAX_VIS = 8
AC_DROP_W  = 250
AC_DOC_W   = 260

AC_KIND_STYLE = {
    "fn":    ((255, 210,  70), "f"),
    "bi":    (( 86, 156, 214), "b"),
    "snip":  ((197, 134, 192), "s"),
    "kw":    ((150, 155, 185), "k"),
    "param": ((206, 145, 120), "p"),
}

# ── Colores de pinguinos ────────────────────────────────
PENGUIN_COLORS = [
    CUI_CYAN,
    CUI_ORANGE,
    (200,  80, 200),
    ( 80, 200,  80),
    (200, 200,  80),
]

COMP_POSITIONS = [(7, 10)]

# ── Hambre ──────────────────────────────────────────────
HUNGER_MAX        = 100.0
HUNGER_PER_FISH   = 20.0
HUNGER_DRAIN_SEC  = 1.0
FISH_CONSUME_SEC  = 10.0
HUNGER_DEATH_MS   = 10_000

NIDO_COST_MADERA = 20
NIDO_COST_HIELO  = 50
FISH_PROBABILITY = 0.40
