import os
from dotenv import load_dotenv

load_dotenv()


# Database
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# OpenVPN sample file
OPENVPN_SAMPLE_FILE_PATH = "./openvpn-sample.ovpn"

# Freeradiud
FREERADIUS_EXPIRATION_DATE_FORMAT = os.getenv("FREERADIUS_EXPIRATION_DATE_FORMAT")
