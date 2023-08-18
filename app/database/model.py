import enum
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, CHAR, Enum, Text
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER, BIGINT, DATETIME

from .base import Base


class OpenVPNProtocol(str, enum.Enum):
    tcp4 = "tcp4"
    udp4 = "udp4"
    tcp6 = "tcp6"
    udp6 = "udp6"


class OpenVPNServer(Base):
    __tablename__ = "openvpn_servers"

    id = Column(Integer, primary_key=True)
    ip = Column(String(255))
    port = Column(Integer)
    protocol = Column(Enum(OpenVPNProtocol), default=OpenVPNProtocol.tcp4)
    x509_name = Column(String(255))
    ca = Column(Text)
    tls_crypt = Column(Text)


class RadCheck(Base):
    __tablename__ = "radcheck"

    id = Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(64), nullable=False, default='', unique=False)
    attribute = Column(String(64), nullable=False, default='')
    op = Column(CHAR(2), nullable=False, default='==')
    value = Column(String(253), nullable=False, default='')
#
#
# class RadAcct(Base):
#     __tablename__ = "radacct"
#
#     radacctid = Column(BIGINT(21), primary_key=True, nullable=False, autoincrement=True)
#     acctsessionid = Column(VARCHAR(64), nullable=False, default='')
#     acctuniqueid = Column(VARCHAR(32), nullable=False, default='')
#     username = Column(VARCHAR(64), nullable=False, default='')
#     groupname = Column(VARCHAR(64), nullable=False, default='')
#     realm = Column(VARCHAR(64), default='')
#     nasipaddress = Column(VARCHAR(15), nullable=False, default='')
#     nasportid = Column(VARCHAR(15), default=None)
#     nasporttype = Column(VARCHAR(32), default=None)
#     acctstarttime = Column(DATETIME, default=None)
#     acctupdatetime = Column(DATETIME, default=None)
#     acctstoptime = Column(DATETIME, default=None)
#     acctinterval = Column(INTEGER(12), default=None)
#     acctsessiontime = Column(INTEGER(12, unsigned=True), default=None)
#     acctauthentic = Column(VARCHAR(32), default=None)
#     connectinfo_start = Column(VARCHAR(50), default=None)
#     connectinfo_stop = Column(VARCHAR(50), default=None)
#     acctinputoctets = Column(BIGINT(20), default=None)
#     acctoutputoctets = Column(BIGINT(20), default=None)
#     calledstationid = Column(VARCHAR(50), nullable=False, default='')
#     callingstationid = Column(VARCHAR(50), nullable=False, default='')
#     acctterminatecause = Column(VARCHAR(32), nullable=False, default='')
#     servicetype = Column(VARCHAR(32), default=None)
#     framedprotocol = Column(VARCHAR(32), default=None)
#     framedipv6address = Column(VARCHAR(32), default=None)
#     framedipv6prefix = Column(VARCHAR(32), default=None)
#     framedinterfaceid = Column(VARCHAR(32), default=None)
#     delegatedipv6prefix = Column(VARCHAR(32), default=None)
#     framedipaddress = Column(VARCHAR(15), nullable=False, default='')

