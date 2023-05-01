import asyncio
from mppong.message import Message
from asyncio import IncompleteReadError


class ProtocolError(Exception):
    pass


class Communication:
    def __init__(self, name, reader, writer, encoding="utf-8", recipient=None):
        self._name = name
        self._recipient = recipient
        self._writer = writer
        self._reader = reader
        self.encoding = encoding
        self.connection_up = True

    async def send_message(self, action, content=None):
        self._set_message(action, content)
        await self._send_header()
        await self._send_content()

    def _set_message(self, action, content):
        self.message = Message(self._name, action, content, self.encoding)
        self.message.set_message()

    async def _send_header(self):
        await self._send_headersize()
        await self._send(self.message.header_dump)

    async def _send_headersize(self):
        message = self.message._get_header_size_message()
        await self._send(message)

    async def _send_content(self):
        if self.message.is_content_to_send():
            await self._send(self.message.content_dump)

    async def _send(self, message):
        try:
            self._writer.write(message)
            await self._writer.drain()
        except Exception as e:
            print(f"Problem while sending {message}: {e}")

    async def read_message(self):
        self.message = Message()
        await self._get_header_content()
        if self.message.is_message() is not None:
            return self.message
        return None

    async def _get_header_content(self):
        await self._get_header()
        self.content = await self._get_content()

    async def _get_header(self):
        await self._get_header_size()
        if self.message.header_size is not None:
            try:
                self.message.header = await asyncio.wait_for(
                        self._reader.read(self.message.header_size), 2)
            except Exception as e:
                print(f"Problem while getting header: {e}")
        else:
            await self.close()

    async def _get_header_size(self):
        try:
            rcpt =  await asyncio.wait_for(self._reader.read(30), 120)
            self.message.header_size = rcpt
        except IncompleteReadError as e:
            print(f"Can't read the expected protoheader {e}")
            await self.close()
        except Exception as e:
            print(f"Problem with protoheader {e}")
            await self.close()

    async def _get_content(self):
        try:
            if self.message.is_content_to_read():
                self.message.content = (await self._reader.read(
                    self.message.content_size))
        except Exception as e:
            print(f"Problem while getting content: {e}")

    def get_recipient_name(self):
        if self.message.header is not None:
            return self.message.header["name"]

    async def close(self):
        self.connection_up = False
        self._writer.close()
        await self._writer.wait_closed()

    def __repr__(self):
        if isinstance(self._recipient, str):
            return_value = f"Name: {self._name} Recipient {self._recipient}\n" \
                           f"writer: {self._writer}, reader: {self._reader}"
        else:
            return_value = f"Name: {self._name} Recipient unknown yet\n" \
                           f"writer: {self._writer}, reader: {self._reader}"
        return return_value
