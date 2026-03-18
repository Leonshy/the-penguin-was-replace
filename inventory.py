# ═══════════════════════════════════════════════════════
#  THE PENGUIN WAS REPLACE — inventory.py
#  Almacen global con capacidad maxima de 500 por recurso
# ═══════════════════════════════════════════════════════

STORAGE_MAX = 1000   # capacidad maxima del almacen por recurso


class Resource:
    def __init__(self, nombre: str, cantidad: int = 0):
        self.nombre   = nombre
        self.cantidad = cantidad

    def agregar(self, n: int = 1):
        self.cantidad = min(STORAGE_MAX, self.cantidad + n)

    def consumir(self, n: int = 1) -> bool:
        if self.cantidad >= n:
            self.cantidad -= n
            return True
        return False

    def is_full(self) -> bool:
        return self.cantidad >= STORAGE_MAX

    def __repr__(self):
        return f"{self.nombre}:{self.cantidad}/{STORAGE_MAX}"


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

    def agregar(self, nombre: str, qty: int = 1) -> int:
        """Agrega qty al recurso. Devuelve cuanto se agrego realmente."""
        r = self.rs.get(nombre)
        if r is None:
            return 0
        before = r.cantidad
        r.agregar(qty)
        return r.cantidad - before

    def consumir(self, nombre: str, qty: int = 1) -> bool:
        r = self.rs.get(nombre)
        return r.consumir(qty) if r else False

    def obtener(self, nombre: str) -> int:
        r = self.rs.get(nombre)
        return r.cantidad if r else 0

    def hud(self) -> str:
        return "   ".join(
            f"{r.nombre}:{r.cantidad}/{STORAGE_MAX}"
            for r in self.rs.values()
        )