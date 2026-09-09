# assets.py — centrální loader + cache, jednou načte, vždy vrátí stejný objekt

import pygame
import os

class Assets:
    _cache = {}

    @classmethod
    def image(cls, path: str) -> pygame.Surface:
        if path not in cls._cache:
            cls._cache[path] = pygame.image.load(path).convert_alpha()
        return cls._cache[path]

    @classmethod
    def sound(cls, path: str) -> pygame.mixer.Sound:
        if path not in cls._cache:
            cls._cache[path] = pygame.mixer.Sound(path)
        return cls._cache[path]

    @classmethod
    def font(cls, path: str | None, size: int) -> pygame.font.Font:
        key = (path, size)
        if key not in cls._cache:
            cls._cache[key] = pygame.font.Font(path, size)
        return cls._cache[key]

    @classmethod
    def clear(cls):
        cls._cache.clear()
