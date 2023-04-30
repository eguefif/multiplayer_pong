import pytest
import asyncio
from mppong.communication import Communication
from mppong.game_elements import Racket

@pytest.fixture
def message():
    player = dict(name="test", local=True, winner=False, side="left")
    racket = Racket(player, 150, 15, 15,
                1500, 800)
    return ("echo", dict(racket=racket))


async def create_connections():
    connections = []
    for i in range(10):
        reader, writer = await asyncio.open_connection("127.0.0.1", 8000)
        communication = Communication(f"Client {i}", writer, reader)
        connections.append(communication)
    return connections

async def close_connections(connections):
    for connection in connections:
        await connection.close()

@pytest.mark.asyncio
async def test_echoserver(message):
    connections = await create_connections()
    answers = []
    for connection in connections:
        await connection.send_message(message[0], message[1])
    for connection in connections:
        answers.append(await connection.read_message())

    for answer in answers:
        assert answer["header"]["action"] == message[0]
        assert answer["content"] == message[1]
    await close_connections(connections)

@pytest.mark.asyncio
async def test_echoserver_two_messages(message):
    connections = await create_connections()
    answers = []
    for connection in connections:
        await connection.send_message(message[0], message[1])
        await connection.send_message(message[0], message[1])
        answers.append(await connection.read_message())
        answers.append(await connection.read_message())

    for answer in answers:
        assert answer["header"]["action"] == message[0]
        assert answer["content"] == message[1]
    await close_connections(connections)
