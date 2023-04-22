from engine import GameEngine
import pygame

pygame.init()
print("Do you want to player (1)alone or (2) multiplayer?")
game_engine = GameEngine()
if input(">") == 1:
    game_engine.run()
else:
    client = Client()
    client.run()
