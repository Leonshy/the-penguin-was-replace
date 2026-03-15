from enum import Enum, auto


class EstadoJuego(Enum):
    JUGANDO = auto()
    PAUSA = auto()
    TERMINADO = auto()