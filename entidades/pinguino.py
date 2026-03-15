from dataclasses import dataclass, field


@dataclass
class Pinguino:
    x: int
    y: int
    energia: int = 100
    inventario: dict = field(default_factory=lambda: {"pez": 0})
    capacidad_inventario: int = 5

    def mover(self, dx: int, dy: int, mapa) -> None:
        nuevo_x = self.x + dx
        nuevo_y = self.y + dy

        if mapa.es_transitable(nuevo_x, nuevo_y):
            self.x = nuevo_x
            self.y = nuevo_y

    def inventario_lleno(self) -> bool:
        return sum(self.inventario.values()) >= self.capacidad_inventario

    def recolectar(self, mapa) -> bool:
        if self.inventario_lleno():
            return False

        recolectado = mapa.quitar_recurso_en(self.x, self.y)
        if recolectado:
            self.inventario["pez"] += 1
            return True
        return False