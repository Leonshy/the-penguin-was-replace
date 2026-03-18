# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — save.py
#  Sistema de guardado y carga de partida (JSON)
# ═══════════════════════════════════════════════════════
from __future__ import annotations
import json
import os

SAVE_PATH = "savegame.json"


def save_game(game) -> bool:
    """Serializa el estado del juego a savegame.json. Devuelve True si OK."""
    try:
        comp = game.computers[0]
        data = {
            "cam_col": game.cam_col,
            "cam_row": game.cam_row,
            "inventory": {
                "Pez":    game.inventory.obtener("Pez"),
                "Madera": game.inventory.obtener("Madera"),
                "Hielo":  game.inventory.obtener("Hielo"),
            },
            "progress": {
                "fish_caught_total": game.progress.fish_caught_total,
                "unlocked":          list(game.progress._unlocked),
            },
            "world": {
                "unlocked_zones": list(game.world.unlocked_zones),
                "nidos": [
                    [r, c]
                    for r in range(len(game.world.grid))
                    for c in range(len(game.world.grid[r]))
                    if game.world.grid[r][c].tipo == "nido"
                ],
            },
            "colony": {
                "hunger": game.colony.hunger,
                "nidos":  game.colony.nidos,
            },
            "penguins": [
                {
                    "nombre":  p.nombre,
                    "row":     p.row,
                    "col":     p.col,
                    "script":  "\n".join(p.win.lines) if p.win else "",
                    "running": bool(p.win and p.win.running),
                }
                for p in game.penguins if p.alive
            ],
            "terminal": {
                "estado":         comp.estado,
                "unlocked_files": list(comp._unlocked_files),
            },
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[SAVE] Error: {e}")
        return False


def load_game() -> dict | None:
    """Carga savegame.json. Devuelve el dict o None si no existe/falla."""
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[LOAD] Error: {e}")
        return None


def save_exists() -> bool:
    return os.path.exists(SAVE_PATH)
