# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — config.py
#  Constantes globales, colores y paleta
# ═══════════════════════════════════════════════════════

# ── Mundo ───────────────────────────────────────────────
T      = 64          # tile size (px)
WW     = 21          # world width  (tiles)
WH     = 14          # world height (tiles)
VW     = 10          # viewport cols visibles
VH     = 9           # viewport rows visibles
WIN_W  = VW * T      # 640 px
HUD_H  = 80          # barra superior
BAR_H  = 20          # barra inferior
WIN_H  = VH * T + HUD_H + BAR_H
FPS    = 30

# ── Velocidad del pinguino ──────────────────────────────
MOVE_DELAY   = 4     # ticks por paso (30fps → ~7 pasos/seg)
ACTION_DELAY = 8     # ticks extra al llegar al destino (animacion de accion)

# ── Paleta UI ───────────────────────────────────────────
CUI_BG     = ( 10,  10,  20)
CUI_WHITE  = (220, 220, 235)
CUI_CYAN   = (  0, 210, 210)
CUI_GREEN  = ( 50, 200,  80)
CUI_GRAY   = ( 80,  80, 100)
CUI_ORANGE = (255, 160,  40)
CUI_RED    = (220,  60,  60)
CUI_BLACK  = (  0,   0,   0)

# ── Colores de tiles ────────────────────────────────────
TILE_COLORS = {
    "f_pesca"    : ( 12,  32,  50),
    "f_bosque"   : ( 10,  38,  14),
    "f_mina"     : ( 30,  30,  42),
    "f_almacen"  : ( 24,  18,  50),
    "f_fabrica"  : ( 10,  38,  46),
    "f_yermo"    : ( 22,  22,  28),
    "agua"       : ( 18,  55, 168),
    "costa"      : (  0, 148, 148),
    "arbol"      : ( 28, 118,  28),
    "mina"       : ( 78,  82, 108),
    "almacen"    : ( 55,  50,  95),
    "fabrica"    : ( 38, 112, 122),
    "computadora": ( 48,  55, 192),
}

# ── Paleta IDE ──────────────────────────────────────────
IDE_BG     = ( 30,  31,  48)
IDE_DARK   = ( 22,  22,  38)
IDE_TITLE  = ( 38,  40,  62)
IDE_HL     = ( 38,  44,  70)
IDE_LNBG   = ( 22,  24,  40)
IDE_BORDER = ( 68,  74, 122)
IDE_CURSOR = (210, 218, 255)
IDE_SEP    = ( 46,  50,  86)
IDE_OUT    = ( 14,  15,  28)

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
AC_BG      = ( 32,  33,  52)
AC_BORDER  = ( 68,  74, 122)
AC_SEL_BG  = ( 50,  90, 148)
AC_DOC_BG  = ( 25,  26,  42)
AC_ITEM_H  = 20
AC_MAX_VIS = 8
AC_DROP_W  = 230
AC_DOC_W   = 240

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

# ── Solo la zona de PESCA tiene computadora ─────────────
# Coordenadas (row, col) segun el nuevo layout:
#   Pesca: r6-9, c7-13  → PC en (7, 10)
COMP_POSITIONS = [(7, 10)]