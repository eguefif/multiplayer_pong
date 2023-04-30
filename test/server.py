import signal
import json
import random
import asyncio
from functools import partial
from asyncio import StreamReader, StreamWriter
from .mppong import GameEngine
from multiplayer_pong.mppong import Racket, Game
from multiplayer_pong.mppong import Communication, ProtocolError

class GracefulExit(SystemExit):
    pass

class Server:
    def __init__(self):
        self._clients = []
        self._connections = []

    async def _add_client(self, reader, writer):
        print("New connection")
        client_communication = Communication("server", writer, reader)
        self._clients.append(client_communication)
        self._connections.append(
                asyncio.create_task(self._listen_client(client_communication)))

    async def _listen_client(self, client_communication):
        while client_communication.connection_up:
            message = await self._get_one_message()
            if message is None:
                break
            self.messages.append(message)
            if (self._message["header"]["action"] == "end_connection"):
                break
        await client_communication.close()

    async def _get_one_message(self):
        try:
            message = await asyncio.wait_for(client_communication.read_message(), 10000)
        except Exception as e:
            print(f"Problem while getting message {e}")
            await client_communication.close()
            return
        return message

    async def _closing(self):
        print("Shuttingdown the server")
        self.server.close()
        await self.server.wait_closed()
        if len(self._clients) > 0:
            for client in self._clients:
                if not client._writer.is_closing:
                    client._connexion_up = False
                    await client.send_message("end_connection")
                    await client.close()
        if len(self._connections) > 0:
            for connection in self._connections:
                connection.cancel()
                if connection.cancelled():
                    print("Connection was terminated")

    def _shutdown(self):
        raise GracefulExit()

    async def start_to_serve(self):
        self.server = await asyncio.start_server(self._add_client, "127.0.0.1", 8000)
        loop = self.server.get_loop()
        loop.add_signal_handler(signal.SIGINT, self._shutdown)
        loop.add_signal_handler(signal.SIGTERM, self._shutdown)
        async with self.server:
            try:
                await self.server.serve_forever()
            except GracefulExit:
                pass
            except Exception as e:
                print(f"Problen {e}")
            finally:
                await self._closing()

server = Server()
asyncio.run(server.start_to_serve())
