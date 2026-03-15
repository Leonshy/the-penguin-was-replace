import pygame
from core.juego import Juego


def main() -> None:
    pygame.init()
    juego = Juego()
    juego.ejecutar()
    pygame.quit()


if __name__ == "__main__":
    main()