import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

# Database
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# OpenVPN sample file
OPENVPN_SAMPLE_FILE_PATH = "./openvpn-sample.ovpn"

# Freeradius
FREERADIUS_EXPIRATION_DATE_FORMAT = os.getenv("FREERADIUS_EXPIRATION_DATE_FORMAT")
