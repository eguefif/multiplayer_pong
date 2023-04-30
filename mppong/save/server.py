import signal
import asyncio
from communication import Communication


class GracefulExit(SystemExit):
    pass


class Server:
    def __init__(self):
        self._clients = []
        self._connection_tasks = []

    async def _add_client(self, reader, writer):
        print("New connection")
        client_communication = Communication("server", writer, reader)
        self._clients.append(client_communication)
        self._connection_tasks.append(
                asyncio.create_task(self._listen_client(client_communication)))

    async def _listen_client(self, client_communication):
        while client_communication.connection_up:
            if (message := await self._get_one_message(client_communication)) == None:
                break
            await self._dispatch_message(message, client_communication)
        await client_communication.close()

    async def _get_one_message(self, client_communication):
        try:
            message = await client_communication.read_message()
        except Exception as e:
            print(f"Problem while getting message {e}")
            await client_communication.close()
            return
        return message

    async def _dispatch_message(self, message, client_communication):
        action = self._get_action_from_header(message)
        if action == "echo":
            await client_communication.send(message)
        elif action == "end_connection":
            client_communication.connection_up = False

    def _get_action_from_header(self, message):
        return message["header"]["action"]

    async def _closing(self):
        print("Shuttingdown the server")
        await self._close_server()
        await self._close_communications()
        self._cancel_tasks()

    async def _close_server(self):
        self.server.close()
        await self.server.wait_closed()

    async def _close_communications(self):
        if len(self._clients) > 0:
            for client in self._clients:
                if not client._writer.is_closing:
                    client._connexion_up = False
                    await client.send_message("end_connection")
                    await client.close()

    def _cancel_tasks(self):
        if len(self._connection_tasks) > 0:
            for connection in self._connections:
                connection.cancel()
                if connection.cancelled():
                    print("Connection was terminated")

    def _shutdown(self):
        raise GracefulExit()

    async def start_to_serve(self):
        self.server = await asyncio.start_server(
                self._add_client, "127.0.0.1", 8000)
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
