from dataclasses import dataclass
from enum import Enum, auto


class TipoCasilla(Enum):
    HIELO = auto()
    AGUA = auto()
    GRIETA = auto()
    BASE = auto()


@dataclass
class Casilla:
    x: int
    y: int
    tipo: TipoCasilla = TipoCasilla.HIELO
    tiene_recurso: bool = False

    def es_transitable(self) -> bool:
        return self.tipo in {TipoCasilla.HIELO, TipoCasilla.BASE}