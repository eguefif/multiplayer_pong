import asyncio
import pytest
from multiprocessing import Process
from mppong.communication import Communication
from mppong.game_elements import Racket, Ball


class TestCommunication:
    @pytest.fixture
    def racket(self):
        player = dict(name="test", local=True, winner=False, side="left")
        return {"racket": Racket(player, 150, 15, 15,
                1500, 800)}

    @pytest.fixture
    def ball_and_racket(self):
        player = dict(name="test", local=True, winner=False, side="left")
        racket =  Racket(player, 150, 15, 15,
                1500, 800)
        ball =  Ball(750, 400, 40, 3)
        return {"ball": ball, "racket": racket}

    @pytest.mark.asyncio
    async def test_with_content_racket(self, racket):
        reader, writer = await asyncio.open_connection(
                "127.0.0.1", 8000)
        communication = Communication("client", reader, writer)
        await communication.send_message("echo", racket)
        message = await communication.read_message()
        assert message.action == "echo"
        assert message.content["racket"] == racket["racket"]

    @pytest.mark.asyncio
    async def test_with_content_ball_and_racket(self, ball_and_racket):
        reader, writer = await asyncio.open_connection(
                "127.0.0.1", 8000)
        communication = Communication("client", reader, writer)
        await communication.send_message("echo", ball_and_racket)
        message = await communication.read_message()
        assert message.action == "echo"
        assert message.content["racket"] == ball_and_racket["racket"]
        assert message.content["ball"] == ball_and_racket["ball"]
