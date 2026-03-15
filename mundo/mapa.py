import random
from mundo.casilla import Casilla, TipoCasilla
from entidades.recurso import Recurso, TipoRecurso
from config import FILAS, COLUMNAS


class Mapa:
    def __init__(self) -> None:
        self.filas = FILAS
        self.columnas = COLUMNAS
        self.grilla = [
            [Casilla(x, y) for x in range(self.columnas)]
            for y in range(self.filas)
        ]
        self.recursos: list[Recurso] = []
        self.generar_mapa()

    def generar_mapa(self) -> None:
        for y in range(self.filas):
            for x in range(self.columnas):
                casilla = self.grilla[y][x]

                if random.random() < 0.08:
                    casilla.tipo = TipoCasilla.GRIETA
                elif random.random() < 0.04:
                    casilla.tipo = TipoCasilla.AGUA
                else:
                    casilla.tipo = TipoCasilla.HIELO

        # zona segura inicial
        for y in range(1, 5):
            for x in range(1, 5):
                self.grilla[y][x].tipo = TipoCasilla.HIELO

        # recursos
        for _ in range(18):
            x = random.randint(0, self.columnas - 1)
            y = random.randint(0, self.filas - 1)

            if self.grilla[y][x].tipo == TipoCasilla.HIELO:
                self.recursos.append(Recurso(x, y, TipoRecurso.PEZ))
                self.grilla[y][x].tiene_recurso = True

    def obtener_casilla(self, x: int, y: int) -> Casilla | None:
        if 0 <= x < self.columnas and 0 <= y < self.filas:
            return self.grilla[y][x]
        return None

    def es_transitable(self, x: int, y: int) -> bool:
        casilla = self.obtener_casilla(x, y)
        return casilla is not None and casilla.es_transitable()

    def quitar_recurso_en(self, x: int, y: int) -> bool:
        for recurso in self.recursos:
            if recurso.x == x and recurso.y == y and not recurso.recolectado:
                recurso.recolectado = True
                casilla = self.obtener_casilla(x, y)
                if casilla:
                    casilla.tiene_recurso = False
                return True
        return False