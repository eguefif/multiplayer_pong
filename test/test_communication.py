import asyncio
import pytest
from multiprocessing import Process
from mppong.communication import Communication
from mppong.game_elements import Racket, Ball


class TestCommunication:
    @pytest.fixture
    def racket(self):
        player = dict(name="test", local=True, winner=False, side="left")
        return Racket(player, 150, 15, 15,
                1500, 800)

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
        communication = Communication("client", writer, reader)
        await communication.send_message("update_racket", dict(racket=racket))
        message = await communication.read_message()
        assert message["header"]["action"] == "update_racket"
        assert message["content"]["racket"] == racket

    @pytest.mark.asyncio
    async def test_with_content_ball_and_racket(self, ball_and_racket):
        reader, writer = await asyncio.open_connection(
                "127.0.0.1", 8000)
        communication = Communication("client", writer, reader)
        await communication.send_message("update_ball_racket", ball_and_racket)
        message = await communication.read_message()
        assert message["header"]["action"] == "update_ball_racket"
        assert message["content"]["racket"] == ball_and_racket["racket"]
        assert message["content"]["ball"] == ball_and_racket["ball"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "action",
        ["create_game","delete_game", "get_list_games",
        "join_game", "update_racket", "update_game", "update_ball_racket",
        "end_communication", "reconnect_game"])
    async def test_communication(self, action):
        reader, writer = await asyncio.open_connection(
                "127.0.0.1", 8000)
        communication = Communication("client", writer, reader)
        await communication.send_message(action)
        message = await communication.read_message()
        assert action == message["header"]["action"]
