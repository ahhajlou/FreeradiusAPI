# import os
from fastapi import FastAPI
from config import OPENVPN_SAMPLE_FILE_PATH

app = FastAPI()


class OpenVPNSample:  # static class shared between all apps
    content: str = ""


def read_openvpn_file():
    with open(OPENVPN_SAMPLE_FILE_PATH) as f:
        return f.read()


@app.on_event("startup")
def on_startup():
    OpenVPNSample.content = read_openvpn_file()


from app import api # noqa