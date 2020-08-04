from cloudmonitor.influx.model_base import *


class NatPm(ModelBase):
    logTime = Column(Index.FIELD)
    uuid = Column(Index.TAG)
    connectNum = Column(Index.FIELD)
    dataPacketInNum = Column(Index.FIELD)
    dataPacketOutNum = Column(Index.FIELD)
    bandwidthIn = Column(Index.FIELD)
    bandwidthOut = Column(Index.FIELD)
    dataSource = Column(Index.FIELD)
    ftp_id = Column(Index.FIELD)


class IpsecVpnPm(ModelBase):
    logTime = Column(Index.FIELD)
    uuid = Column(Index.TAG)
    bandwidthInTotal = Column(Index.FIELD)
    bandwidthOutTotal = Column(Index.FIELD)
    dataPacketInNumTotal = Column(Index.FIELD)
    dataPacketOutNumTotal = Column(Index.FIELD)
    dataSource = Column(Index.FIELD)
    ftp_id = Column(Index.FIELD)


class VlbPm(ModelBase):
    createTime = Column(Index.FIELD)
    uuid = Column(Index.TAG)
    trafficIn = Column(Index.FIELD)
    trafficOut = Column(Index.FIELD)
    requestsTotal = Column(Index.FIELD)
    activeCon = Column(Index.FIELD)
    ftp_id = Column(Index.FIELD)


class VlbListenerPm(ModelBase):
    createTime = Column(Index.FIELD)
    uuid = Column(Index.TAG)
    trafficIn = Column(Index.FIELD)
    trafficOut = Column(Index.FIELD)
    requestsTotal = Column(Index.FIELD)
    activeCon = Column(Index.FIELD)
    estabCon = Column(Index.FIELD)
    packetIn = Column(Index.FIELD)
    packetOut = Column(Index.FIELD)
    abandonCon = Column(Index.FIELD)
    httpQps = Column(Index.FIELD)
    ftp_id = Column(Index.FIELD)
