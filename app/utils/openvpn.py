from io import StringIO
from jose import JWTError
from fastapi import Security, HTTPException
from fastapi.responses import Response, StreamingResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT

from app import OpenVPNSample
from app.utils.jwt import create_access_token, decode_access_token
from config import BASE_URL


class OpenVPNConfigFile:
    def __init__(self, username: str = None, server: str = None, token: str = None):
        self.file_name = "file"
        self.username = username
        self.server = server
        self.token = token
        self.config: str = ""

    def generate_config(self, server):
        self.config = OpenVPNSample.content.format(
            OPENVPN_PROTOCOL="tcp-client",
            SERVER_IP="1.1.1.1",
            SERVER_PORT="8080",
            X509_NAME="Test",
            OPENVPN_CA="Empty",
            OPENVPN_TLS_CRYPT="Empty"

        )

    def stream_response(self) -> StreamingResponse:
        server = self.check_access_and_get_server()
        self.generate_config(server)
        string_io = StringIO(self.config)
        string_io.seek(0)

        def io_iter():
            with string_io as f:
                yield from f.read()

        headers = {
            'Content-Disposition': f'inline; filename="{self.file_name}.ovpn"',
            'content-type': 'application/octet-stream'
        }
        return StreamingResponse(io_iter(), headers=headers, media_type="text/plain")

    def file_response(self):
        server = self.check_access_and_get_server()
        self.generate_config(server)
        response_headers = {
            "content-disposition": f'attachment; filename="{self.file_name}".ovpn',
        }

        return Response(content=self.config, media_type="text/plain", headers=response_headers)

    def text_response(self) -> str:
        return self.config

    def download_url(self) -> str:
        return f"{BASE_URL}/download/openvpn/{self.create_jwt_token()}"

    def create_jwt_token(self):
        data = dict()
        data.update(username=self.username, server=self.server)
        token = create_access_token(data)
        return token

    def check_access_and_get_server(self):
        try:
            data = decode_access_token(self.token)
            if server := data.get("server"):
                return server
            else:
                raise HTTPException(status_code=HTTP_204_NO_CONTENT)
        except JWTError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN)

