from enum import Enum, auto


class TipoTarea(Enum):
    IDLE = auto()
    PESCAR = auto()
    VOLVER_BASE = auto()
    EXPLORAR = auto()