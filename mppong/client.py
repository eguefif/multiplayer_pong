from communication import Communication
from engine import GameEngine
import asyncio
from asyncio import Queue
import sys

class ClientPong:
    def __init__(self, name):
        self.host = "127.0.0.1"
        self.port = 8000
        self.name = name
        self._connection_up = True

    async def run(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        server_communication = Communication(self.name, "server", writer, reader) 
        stdin_reader = await self._create_stdin_reader()
        listener_task = asyncio.create_task(self.listen_server(server_communication))
        writer_task = asyncio.create_task(self.listen_input(server_communication, stdin_reader))
        await asyncio.wait([listener_task,
                writer_task],
                return_when=asyncio.FIRST_COMPLETED,
                )

    async def listen_server(self, server_communication):
        while server_communication.connection_up:
            listen_task = asyncio.create_task(server_communication.read_message())
            try:
                message = await asyncio.wait_for(listen_task, 10000)
                if message is None:
                    break
            except Exception as e:
                print(f"Problem while reading {e}")
                await server_communication.close()
            else:
                if message["header"] is not None:
                    if message["header"]["action"] == "end_connection":
                        self._connection_up = False
                        print("terminating connection")
                        await server_communication.close()
                    print(message["header"]["action"])
        await server_communication.close()

    async def listen_input(self, server_communication, stdin_reader):
        action = None
        try:
            while self._connection_up and action != "end_connection":
                    action = await stdin_reader.readline()
                    await server_communication.send_message(action.decode("utf-8").strip())
        except Exception as e:
            print(f"Problem while writing {e}")
        finally:
            tasks = asyncio.all_tasks()
            for task in tasks:
                task.cancel()
            await server_communication.close()

    async def _create_stdin_reader(self):
        stream_reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(stream_reader)
        loop = asyncio.get_running_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        return stream_reader

if __name__ == "__main__":
    client = ClientPong("Manu")
    asyncio.run(client.run())
