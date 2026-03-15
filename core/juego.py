import sys
import pygame

from config import ANCHO_VENTANA, ALTO_VENTANA, FPS, TITULO
from core.estado_juego import EstadoJuego
from mundo.mapa import Mapa
from entidades.pinguino import Pinguino
from entidades.colonia import Colonia
from ui.render import Render


class Juego:
    def __init__(self) -> None:
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.estado = EstadoJuego.JUGANDO

        self.mapa = Mapa()
        self.colonia = Colonia(2, 2)
        self.pinguino = Pinguino(3, 3)

        self.render = Render(self.pantalla)

    def procesar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if evento.key == pygame.K_UP:
                    self.pinguino.mover(0, -1, self.mapa)
                elif evento.key == pygame.K_DOWN:
                    self.pinguino.mover(0, 1, self.mapa)
                elif evento.key == pygame.K_LEFT:
                    self.pinguino.mover(-1, 0, self.mapa)
                elif evento.key == pygame.K_RIGHT:
                    self.pinguino.mover(1, 0, self.mapa)
                elif evento.key == pygame.K_SPACE:
                    self.pinguino.recolectar(self.mapa)

    def actualizar(self) -> None:
        pass

    def dibujar(self) -> None:
        self.render.dibujar_todo(self.mapa, self.colonia, self.pinguino)

    def ejecutar(self) -> None:
        while self.estado == EstadoJuego.JUGANDO:
            self.reloj.tick(FPS)
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()