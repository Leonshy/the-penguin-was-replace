from dataclasses import dataclass
from enum import Enum, auto


class TipoRecurso(Enum):
    PEZ = auto()
    HIELO = auto()
    PIEDRA = auto()


@dataclass
class Recurso:
    x: int
    y: int
    tipo: TipoRecurso
    recolectado: bool = False