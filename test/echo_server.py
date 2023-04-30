import asyncio
from mppong.communication import Communication


class EchoServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.tasks = []

    async def _new_connection(self, reader, writer):
        client_communication = self._create_communication_interface(
                writer, reader)
        await self._create_listening_task(client_communication)

    def _create_communication_interface(self, writer, reader):
        client_communication = Communication("server", writer, reader)
        self.clients.append(client_communication)
        return client_communication

    async def _create_listening_task(self, client_communication):
        echo_task = asyncio.create_task(self._echo_task(client_communication))
        self.tasks.append(echo_task)
        await asyncio.gather(echo_task)

    async def _echo_task(self, client_communication):
        message = await client_communication.read_message()
        await client_communication.send_message(message["header"]["action"], message["content"])

    async def _shutdown(self):
        await self._closing_clients_communication()
        await self._close_server()

    async def _closing_clients_communication(self):
        for client in self.clients:
            await client.close()

    async def _close_server(self):
        self.server.close()
        await self.server.wait_closed()

    async def run(self):
        self.server = await asyncio.start_server(self._new_connection,
                                                 self.host, self.port)
        try:
            await self.server.serve_forever()
        except KeyboardInterrupt:
            print("Closing with ^c")
        finally:
            await self._shutdown()


server = EchoServer("127.0.0.1", 8000)
asyncio.run(server.run())
