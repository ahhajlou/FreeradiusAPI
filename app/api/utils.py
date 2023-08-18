from io import StringIO
from fastapi.responses import Response, StreamingResponse

from app import OpenVPNSample


class OpenVPNConfigFile:
    def __init__(self):
        self.file_name = "file"
        self.config = self.generate_config()

    def generate_config(self):
        print(self)
        return OpenVPNSample.content.format(
            OPENVPN_PROTOCOL="tcp-client",
            SERVER_IP="1.1.1.1",
            SERVER_PORT="8080",
            X509_NAME="Test",
            OPENVPN_CA="Empty",
            OPENVPN_TLS_CRYPT="Empty"

        )

    def stream_response(self) -> StreamingResponse:
        self.generate_config()
        string_io = StringIO(self.config)
        string_io.seek(0)

        def io_iter():
            with string_io as f:
                yield from f.read()

        headers = {
            'Content-Disposition': f'inline; filename="{self.file_name}.ovpn"',
            'content-type': 'application/octet-stream'
        }
        return StreamingResponse(io_iter(), headers=headers, media_type="text/txt")

    def text_response(self) -> str:
        return self.config
