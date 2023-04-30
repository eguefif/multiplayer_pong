import asyncio
from mppong.game_elements import Ball, Racket
from asyncio import IncompleteReadError
import json


class ProtocolError(Exception):
    pass


class Communication:
    def __init__(self, name, writer, reader, recipient=None):
        self._name = name
        self._recipient = recipient
        self._writer = writer
        self._reader = reader
        self.encoding = "utf-8"
        self.connection_up = True
        self.header = {}
        self.content = None

    async def send_message(self, action, content=None):
        self._set_message(action, content)
        await self._send_header()
        await self._send_content()
        self._reset_message()

    def _set_message(self, action, content):
        self._set_content(content)
        self._set_header(action)

    def _set_content(self, content):
        if content:
            dict_content = {}
            for key, value in content.items():
                dict_content.update({key: value.__dict__})
            self.content = self._json_encode(dict_content)

    def _json_encode(self, content):
        return json.dumps(content).encode(self.encoding)

    def _set_header(self, action):
        self.header = {"name": self._name,
                       "content_size": self._get_content_size(),
                       "action": action}
        self._build_header_dump()

    def _get_content_size(self):
        if isinstance(self.content, (bytes, bytearray)):
            return len(self.content)
        else:
            return 0

    def _build_header_dump(self):
        self.header_dump = json.dumps(self.header).encode(self.encoding)

    async def _send_header(self):
        await self._send_headersize()
        await self._send(self.header_dump)

    async def _send_headersize(self):
        message = self._build_header_size_message()
        await self._send(message)

    def _build_header_size_message(self):
        header_size = self._get_header_size_for_message()
        return f"{header_size:30}".encode(self.encoding)

    def _get_header_size_for_message(self):
        return len(self.header_dump)

    async def _send_content(self):
        if self.header["content_size"] != 0:
            await self._send(self.content)

    async def _send(self, message):
        try:
            self._writer.write(message)
            await self._writer.drain()
        except Exception as e:
            print(f"Problem while sending {message}: {e}")

    def _reset_message(self):
        self.header = {}
        self.content = None
        self.header_dump = None

    async def read_message(self):
        self.header = {}
        self.content = {}
        await self._get_header_content()
        if self.header is not None:
            return {"header": self.header, "content": self.content}

    async def _get_header_content(self):
        await self._get_header()
        self.content = await self._get_content()

    async def _get_header(self):
        await self._get_header_size()
        if self.header_size is not None:
            try:
                header_dump = await asyncio.wait_for(
                        self._reader.read(self.header_size), 2)
            except Exception as e:
                print(f"Problem while getting header: {e}")
                return
            else:
                self.header = self._json_decode(header_dump)
        else:
            self.header = None

    def _json_decode(self, content):
        return json.loads(content)

    async def _get_header_size(self):
        try:
            self.header_size = (await asyncio.wait_for(self._reader.read(30), 10000)).decode()
        except IncompleteReadError as e:
            print(f"Can't read the expected protoheader {e}")
            await self.close()
        except Exception as e:
            print(f"Problem with protoheader {e}")
            await self.close()
        await self._check_header_size()

    async def _check_header_size(self):
        if self.header_size != '':
            self.header_size = int(self.header_size)
        else:
            print(f"closing connection")
            await self.close()
            self.header_size = None

    async def _get_content(self):
        try:
            if self.header is not None:
                if self.header["content_size"] > 0:
                    content_dump = (await self._reader.read(
                        self.header["content_size"]))
                    self._decode_content_dump(content_dump)
                    return self.content
                else:
                    return None
        except Exception as e:
            print(f"Problem while getting content: {e}")

    def _decode_content_dump(self, content_dump):
        content_decoded = content_dump.decode(self.encoding)
        self._json_loads_content(content_decoded)

    def _json_loads_content(self, content_decoded):
        self.content = {}
        content_loaded = self._json_decode(content_decoded)
        for key, value in content_loaded.items():
            if "racket" in key:
                self.content.update({key: Racket.from_dict(value)})
            elif "ball" in key:
                self.content.update({key: Ball.from_dict(value)})

    def get_recipient_name(self):
        if self.header is None:
            return
        return self.header["name"]

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


class Message:
    def __init__(self, header, content):
        self.header = header
        self.content = content

