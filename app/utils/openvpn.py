from io import StringIO
from jose import JWTError
from fastapi import Security, HTTPException
from fastapi.responses import Response, StreamingResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT

from app import OpenVPNSample
from app.database import query, AsyncSession
from app.utils.jwt import create_access_token, decode_access_token
from config import BASE_URL


class OpenVPNConfigFile:
    def __init__(self, username: str = None, server_ip: str = None, token: str = None):
        self.file_name = "file"
        self.username = username
        self.server_ip = server_ip
        self.token = token
        self.config: str = ""

    async def generate_config(self, server_ip: str, db: AsyncSession):
        openvpn_server = await query.get_server_by_ip(server_ip, db)
        self.config = OpenVPNSample.content.format(
            OPENVPN_PROTOCOL="tcp-client",
            SERVER_IP=openvpn_server.domain,
            SERVER_PORT=openvpn_server.port,
            X509_NAME=openvpn_server.x509_name,
            OPENVPN_CA=openvpn_server.ca,
            OPENVPN_TLS_CRYPT=openvpn_server.tls_crypt

        )

    async def stream_response(self, db: AsyncSession) -> StreamingResponse:
        server_ip = self.check_access_and_get_server_ip()
        await self.generate_config(server_ip, db)
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

    async def file_response(self, db: AsyncSession):
        server_ip = self.check_access_and_get_server_ip()
        await self.generate_config(server_ip, db)
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
        data.update(username=self.username, server_ip=self.server_ip)
        token = create_access_token(data)
        return token

    def check_access_and_get_server_ip(self):
        try:
            data = decode_access_token(self.token)
            if server_ip := data.get("server_ip"):
                return server_ip
            else:
                raise HTTPException(status_code=HTTP_204_NO_CONTENT)
        except JWTError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN)

