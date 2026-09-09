#!/usr/bin/env python3
# main.py — vstupní bod hry

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.game import Game
from src.scenes.menu import MenuScene
from src.scenes.gameplay import GameplayScene


def main():
    game = Game()
    game.register("menu",     MenuScene)
    game.register("gameplay", GameplayScene)
    game.switch("menu")
    game.run()


if __name__ == "__main__":
    main()
