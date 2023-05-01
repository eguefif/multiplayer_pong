import asyncio
from mppong.communication import Communication


class EchoServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.tasks = []

    async def run(self):
        self.server = await asyncio.start_server(self._new_connection,
                                                 self.host, self.port)
        try:
            async with self.server:
                await self.server.serve_forever()
        except KeyboardInterrupt:
            print("Closing with ^c")
        finally:
            await self._shutdown()

    async def _new_connection(self, reader, writer):
        client_communication = self._create_communication_interface(
                reader, writer)
        await self._get_authentification_message(client_communication)

    def _create_communication_interface(self, reader, writer):
        client_communication = Communication("server", reader, writer)
        self.clients.append(client_communication)
        return client_communication

    async def _get_authentification_message(self, client_communication):
        message = await client_communication.read_message() 
        await self._check_credential(message, client_communication)

    async def _check_credential(self, message, client_communication):
        if message.action == "identify":
            client_communication.recipient = message.name
            print("we have authenticate: ", client_communication.recipient)
            await client_communication.send_message("welcome")
            await self._create_listening_task(client_communication)
        else:
            await self._close_one_connection(client_communication)

    async def _create_listening_task(client_communication):
        await self._create_listening_task(client_communication)

    async def _create_listening_task(self, client_communication):
        listening_task = asyncio.create_task(self._listening_task(client_communication))
        self.tasks.append(listening_task)
        await asyncio.gather(listening_task)

    async def _listening_task(self, client_communication):
        while client_communication.connection_up:
            message = await client_communication.read_message()
            if not await self._dispatch_message(message, client_communication):
                break
        await client_communication.close()

    async def _dispatch_message(self, message, client_communication):
        if not message.is_message():
            return False
        elif message.action == "echo":
            await client_communication.send_message(message.action, message.content)
        return True

    async def _shutdown(self):
        await self._close_server()
        await self._closing_clients_communication()
        self._cancelling_task()

    async def _closing_clients_communication(self):
        for client in self.clients:
            if client.connection_up == True:
                await client.close()

    def _cancelling_task(self):
        for task in asyncio.all_tasks():
            task.cancel()

    async def _close_server(self):
        self.server.close()
        await self.server.wait_closed()

    async def _close_one_connection(self, client_communication):
        await client_communication.send_message("end_connection")
        await client_communication.close()


server = EchoServer("127.0.0.1", 8000)
asyncio.run(server.run())
