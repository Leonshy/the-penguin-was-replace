from dataclasses import dataclass, field


@dataclass
class Colonia:
    x: int
    y: int
    peces_almacenados: int = 0
    hielo_almacenado: int = 0
    piedra_almacenada: int = 0
    pinguinos: list = field(default_factory=list)

    def depositar_pez(self, cantidad: int) -> None:
        self.peces_almacenados += cantidad