import asyncio
from asyncio import IncompleteReadError, TimeoutError
import json
import logging

class ProtocolError(Exception):
    pass

class Communication:
    def __init__(self, name, receptor, writer, reader):
        self._name = name
        self._receptor = receptor
        self._writer = writer
        self._reader = reader
        self.encoding = "utf-8"
        self.connection_up = True

    async def send_message(self, action, content=None):
        if content is not None:
            content_dump = self._json_encode(content)
            content_size = len(content_dump)
        else:
            content_size = 0
        header = {"name": self._name,
                  "content_size": content_size,
                  "action": action}
        try:
            header_dump = self._json_encode(header)
        except Exception as e:
            print(f"Problem while dumping header {e}")
        header_size = len(header_dump)
        await self._send_protoheader(header_size)
        await self._send(header_dump)
        if content_size != 0:
            await self._send(content_dump)

    async def _send_protoheader(self, header_size):
        try:
            await self._send(f"{header_size:>30}".encode(self.encoding))
        except Exception as e:
            print(f"Problem while sending protheader: {e}")

    async def _send(self, message):
        try:
            self._writer.write(message)
            await self._writer.drain()
        except Exception as e:
            print(f"Problem while sending {message}: {e}")

    def _json_encode(self, content):
        return json.dumps(content).encode(self.encoding)

    def _json_decode(self, content):
        content_dump = content.decode(self.encoding)
        return json.loads(content)

    async def read_message(self):
        content = None
        header = await self._get_header()
        if header is None:
            return
        try:
            if header["content_size"] > 0:
                content = await asyncio.wait_for(self._get_content(), 2)
        except TimeoutError:
            print("No content")
        return {"header": header, "content": content}

    async def _get_content(self):
        try:
            content_size = self.header["content_size"]
            content_dump = (await self._reader.read(content_size))
        except Exception as e:
            print(f"Problem while getting content: {e}")
            return
        else:
            self.content = self._json_decode(content_dump)
            return self.content

    async def _get_header(self):
        header_size = await self._get_header_size()
        if header_size is not None:
            try:
                header_dump = await asyncio.wait_for(self._reader.read(header_size), 2)
            except Exception as e:
                print(f"Problem while getting header: {e}")
                return
            else:
                self.header = self._json_decode(header_dump)
                return self.header

    async def _get_header_size(self):
        try:
            if (protoheader := await asyncio.wait_for(self._reader.read(30), 10000)) == b"":
                self.connection_up = False
                return
            print(protoheader)
        except IncompleteReadError as e:
            print(f"Can't read the expected protoheader {e}")
            await self.close()
            return
        except Exception as e:
            print(f"Problem with protoheader {e}")
            await self.close()
            return
        else:
            return int(protoheader.decode(self.encoding))

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()
