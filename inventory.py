# ═══════════════════════════════════════════════════════
#  CYBORG PENGUINS — inventory.py
# ═══════════════════════════════════════════════════════


class Resource:
    def __init__(self, nombre: str, cantidad: int = 0):
        self.nombre   = nombre
        self.cantidad = cantidad

    def agregar(self, n: int = 1):
        self.cantidad += n

    def consumir(self, n: int = 1) -> bool:
        if self.cantidad >= n:
            self.cantidad -= n
            return True
        return False

    def __repr__(self):
        return f"{self.nombre}:{self.cantidad}"


class Fish(Resource):
    def __init__(self): super().__init__("Pez")

class Wood(Resource):
    def __init__(self): super().__init__("Madera")

class IceRes(Resource):
    def __init__(self): super().__init__("Hielo")


class Inventory:
    def __init__(self):
        self.rs: dict[str, Resource] = {
            "Pez":    Fish(),
            "Madera": Wood(),
            "Hielo":  IceRes(),
        }

    def agregar(self, nombre: str, qty: int = 1):
        if nombre in self.rs:
            self.rs[nombre].agregar(qty)

    def obtener(self, nombre: str) -> int:
        r = self.rs.get(nombre)
        return r.cantidad if r else 0

    def hud(self) -> str:
        return "   ".join(
            f"{r.nombre}: {r.cantidad}" for r in self.rs.values()
        )
