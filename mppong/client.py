import asyncio
from asyncio import Queue
import sys
from mppong.communication import Communication


class ClientPong:
    def __init__(self, name, host, port):
        self.host = host
        self.port = port
        self.name = name
        self._connection_up = True
        self._server_communication = None

    async def run(self):
        await self._create_server_communication()
        if await self._authetificate():
            await self._create_listening_and_writing_tasks()
        else:
            self._failed_to_authenticate()

    async def _create_server_communication(self):
        self._stdin_reader, reader, writer = await self._return_streams()
        self._server_communication = Communication(
                self.name, reader, writer) 

    async def _return_streams(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        stdin_reader = await self._create_stdin_reader()
        return stdin_reader, reader, writer

    async def _listen_input(self):
        action = None
        try:
            while (self._server_communication.connection_up
                    and action != "end_connection"):
                    action = await self._stdin_reader.readline()
                    await self._server_communication.send_message(
                            action.decode("utf-8").strip())
        except Exception as e:
            print(f"Problem while writing {e}")
            await self._close()
    
    async def _authentificate(self):
        await self._server_communication.send_message("identify")
        if await self._did_authentification_work():
            self._create_listening_and_writing_tasks()
        self._failed_to_authenticate()

    async def _did_authentification_work(self):
        message = await self._server_communication.read_message()
        if message.action == "welcome":
            return True
        return False

    async def _create_listening_and_writing_tasks(self):
        listener_task = asyncio.create_task(self._listen_server())
        writer_task = asyncio.create_task(
                self._listen_input())
        await asyncio.wait([listener_task, writer_task],
                return_when=asyncio.FIRST_COMPLETED)

    async def _listen_server(self):
        while self._server_communication.connection_up:
            message = await self._get_one_message()
            if not message.is_message():
                break
            await self._dispatch_commands(message)
        await self._close()

    async def _get_one_message(self):
        try:
            message = await self._server_communication.read_message()
        except Exception as e:
            print(f"Problem while reading {e}")
            return
        return message

    async def _dispatch_commands(self,message):
        print(message.action)
        if message.action == "end_connection":
            self._server_communication.connection_up = False

    async def _close(self):
        self._cancel_tasks()
        await self._close_communication()

    def _cancel_tasks(self):
        tasks = asyncio.all_tasks()
        for task in tasks:
            task.cancel()

    async def _close_communication(self):
        await self._server_communication.close()

    async def _create_stdin_reader(self):
        stream_reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(stream_reader)
        loop = asyncio.get_running_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        return stream_reader

    async def _failed_to_authenticate(self):
        print("Failure to authenticate")
        self._close()

if __name__ == "__main__":
    client = ClientPong("Manu", "127.0.0.1", 8000)
    asyncio.run(client.run())
