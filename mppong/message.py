import json
from mppong.game_elements import Ball, Racket


class Message:
    def __init__(self, name=None, action=None, content=None, encoding="utf-8"):
        self._name = name
        self._action = action
        self._content = content
        self._encoding = encoding
        self._header_size = None
        self._header = None
        self._header_dump = None
        self._content_dump = None

    @property
    def action(self):
        if self._header is not None:
            return self._header["action"]
        return None

    @property
    def content_size(self):
        if self._header is not None:
            return self._header["content_size"]

    @property
    def header_size(self):
        return self._header_size

    @header_size.setter
    def header_size(self, header_size):
        header_size = header_size.decode(self._encoding)
        if header_size != '':
            self._header_size = int(header_size)
        return None

    @property
    def name(self):
        if self.is_header():
            return self.header["name"]

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        if header is not None:
            self._header = self._json_decode_header(header)

    def _json_decode_header(self, header):
        return json.loads(header.decode(self._encoding))

    @property
    def content_dump(self):
        return self._content_dump

    @property
    def header_dump(self):
        return self._header_dump

    @property
    def content(self):
        if self._content:
            return self._content

    @content.setter
    def content(self, content_dump):
        if content_dump is not None:
            self._decode_content_dump(content_dump)

    def _decode_content_dump(self, content_dump):
        content_decoded = content_dump.decode(self._encoding)
        self._json_loads_content(content_decoded)

    def _json_loads_content(self, content_decoded):
        content_loaded = json.loads(content_decoded)
        self._rebuild_objects_from_dict(content_loaded)

    def _rebuild_objects_from_dict(self, content_loaded):
        self._content = {}
        for key, value in content_loaded.items():
            if "racket" == key:
                self._content.update({key: Racket.from_dict(value)})
            elif "ball" == key:
                self._content.update({key: Ball.from_dict(value)})

    ###########################################
    def is_content_to_read(self):
        if self._header is not None:
            if self._header["content_size"] > 0:
                return True
            return False

    def is_content_to_send(self):
        if self._header["content_size"] > 0:
            return True
        return False

    def is_message(self):
        if self._header is not None:
            return True
        return False

    def is_header(self):
        if self._header_size is not None:
            return True
        return False
    
    ###########################################
    def set_message(self):
        self._set_content()
        self._set_header()
    
    def _set_content(self):
        if self._content:
            dict_content = {}
            for key, value in self._content.items():
                dict_content.update({key: value.__dict__})
            self._content_dump = self._json_encode(dict_content)

    def _json_encode(self, content):
        return json.dumps(content).encode(self._encoding)

    def _set_header(self):
        if self._name and self._action:
            self._header = {"name": self._name,
                           "content_size": self.get_content_dump_size(),
                           "action": self._action}
            self._build_header_dump()

    def get_content_dump_size(self):
        if isinstance(self._content_dump, (bytes, bytearray)):
            return len(self._content_dump)
        else:
            return 0

    def _build_header_dump(self):
        self._header_dump = json.dumps(self.header).encode(self._encoding)

    def _get_header_size_message(self):
        header_size = self._get_header_size_for_message()
        return f"{header_size:30}".encode(self._encoding)

    def _get_header_size_for_message(self):
        return len(self._header_dump)

    def __repr__(self):
        r = f"Message name: {self.name} header: {self._header} content: {self._content}"\
            f"\n header_dump: {self._header_dump}, content_dump: {self._content_dump}"
        return r
