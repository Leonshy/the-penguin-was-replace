import pygame

from config import (
    ANCHO_VENTANA,
    ALTO_VENTANA,
    TAM_CASILLA,
    BLANCO,
    NEGRO,
    AZUL_HIELO,
    AZUL_AGUA,
    GRIS_GRIETA,
    AMARILLO_PEZ,
    ROJO_BASE,
    VERDE_PINGUINO,
)
from mundo.casilla import TipoCasilla


class Render:
    def __init__(self, pantalla: pygame.Surface) -> None:
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("arial", 20)

    def dibujar_todo(self, mapa, colonia, pinguino) -> None:
        self.pantalla.fill(BLANCO)

        self._dibujar_mapa(mapa)
        self._dibujar_colonia(colonia)
        self._dibujar_recursos(mapa)
        self._dibujar_pinguino(pinguino)
        self._dibujar_hud(colonia, pinguino)

        pygame.display.flip()

    def _dibujar_mapa(self, mapa) -> None:
        for fila in mapa.grilla:
            for casilla in fila:
                rect = pygame.Rect(
                    casilla.x * TAM_CASILLA,
                    casilla.y * TAM_CASILLA,
                    TAM_CASILLA,
                    TAM_CASILLA,
                )

                color = AZUL_HIELO
                if casilla.tipo == TipoCasilla.AGUA:
                    color = AZUL_AGUA
                elif casilla.tipo == TipoCasilla.GRIETA:
                    color = GRIS_GRIETA
                elif casilla.tipo == TipoCasilla.BASE:
                    color = ROJO_BASE

                pygame.draw.rect(self.pantalla, color, rect)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 1)

    def _dibujar_recursos(self, mapa) -> None:
        for recurso in mapa.recursos:
            if recurso.recolectado:
                continue

            cx = recurso.x * TAM_CASILLA + TAM_CASILLA // 2
            cy = recurso.y * TAM_CASILLA + TAM_CASILLA // 2
            pygame.draw.circle(self.pantalla, AMARILLO_PEZ, (cx, cy), TAM_CASILLA // 4)

    def _dibujar_colonia(self, colonia) -> None:
        rect = pygame.Rect(
            colonia.x * TAM_CASILLA,
            colonia.y * TAM_CASILLA,
            TAM_CASILLA,
            TAM_CASILLA,
        )
        pygame.draw.rect(self.pantalla, ROJO_BASE, rect)
        pygame.draw.rect(self.pantalla, NEGRO, rect, 2)

    def _dibujar_pinguino(self, pinguino) -> None:
        rect = pygame.Rect(
            pinguino.x * TAM_CASILLA + 6,
            pinguino.y * TAM_CASILLA + 6,
            TAM_CASILLA - 12,
            TAM_CASILLA - 12,
        )
        pygame.draw.ellipse(self.pantalla, VERDE_PINGUINO, rect)

    def _dibujar_hud(self, colonia, pinguino) -> None:
        panel_x = 650
        texto1 = self.fuente.render(
            f"Energia: {pinguino.energia}", True, NEGRO
        )
        texto2 = self.fuente.render(
            f"Peces inventario: {pinguino.inventario['pez']}", True, NEGRO
        )
        texto3 = self.fuente.render(
            f"Peces colonia: {colonia.peces_almacenados}", True, NEGRO
        )
        texto4 = self.fuente.render(
            "Flechas: mover | ESPACIO: recolectar", True, NEGRO
        )

        self.pantalla.blit(texto1, (panel_x, 50))
        self.pantalla.blit(texto2, (panel_x, 90))
        self.pantalla.blit(texto3, (panel_x, 130))
        self.pantalla.blit(texto4, (520, ALTO_VENTANA - 40))