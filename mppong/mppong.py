from client import ClientPong
import random
from engine import GameEngine
import asyncio

def get_players():
    player1 = dict(name=input("First players's name: "), local=True, winner=False)
    player2 = dict(name=input("Second players's name: "), local=True, winner=False)
    choices = ("left", "right")
    player1.update({"side": random.choice(choices)}) 
    if player1["side"] == "left":
        player2.update({"side": "right"})
    else:
        player2.update({"side": "left"})
    return player1, player2

print("Do you want to player (1)alone or (2) multiplayer?")
choice = int(input(">"))
if choice == 1:
    player1, player2 = get_players()
    game_engine = GameEngine(player1, player2)
    game_engine.run()
    if game_engine.get_winner():
        print(f"Winner is {game_engine.get_winner()['name']}")
    else:
        print("No winner")
else:
    name = input("player's name: ")
    client = ClientPong(name)
    asyncio.run(client.run())
