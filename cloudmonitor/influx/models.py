from cloudmonitor.influx.model_base import *


class NatPm(ModelBase):
    LogTime = Column(Index.FIELD)
    Uuid = Column(Index.TAG)
    connectNum = Column(Index.FIELD)
    dataPacketInNum = Column(Index.FIELD)
    dataPacketOutNum = Column(Index.FIELD)
    bandwidthIn = Column(Index.FIELD)
    bandwidthOut = Column(Index.FIELD)
    dataSource = Column(Index.TAG)
    subtask_id = Column(Index.TAG)


class IpsecVpnPm(ModelBase):
    LogTime = Column(Index.FIELD)
    Uuid = Column(Index.TAG)
    bandwidthInTotal = Column(Index.FIELD)
    bandwidthOutTotal = Column(Index.FIELD)
    dataPacketInNumTotal = Column(Index.FIELD)
    dataPacketOutNumTotal = Column(Index.FIELD)
    dataSource = Column(Index.TAG)
    subtask_id = Column(Index.TAG)


class VlbPm(ModelBase):
    CREATE_TIME = Column(Index.FIELD)
    ID = Column(Index.TAG)
    TRAFFIC_IN = Column(Index.FIELD)
    TRAFFIC_OUT = Column(Index.FIELD)
    REQUESTS_TOTAL = Column(Index.FIELD)
    ACTIVE_CON = Column(Index.FIELD)
    subtask_id = Column(Index.TAG)


class VlbListenerPm(ModelBase):
    CREATE_TIME = Column(Index.FIELD)
    ID = Column(Index.TAG)
    TRAFFIC_IN = Column(Index.FIELD)
    TRAFFIC_OUT = Column(Index.FIELD)
    REQUESTS_TOTAL = Column(Index.FIELD)
    ACTIVE_CON = Column(Index.FIELD)
    ESTAB_CON = Column(Index.FIELD)
    PACKET_IN = Column(Index.FIELD)
    PACKET_OUT = Column(Index.FIELD)
    ABANDON_CON = Column(Index.FIELD)
    HTTP_QPS = Column(Index.FIELD)
    subtask_id = Column(Index.TAG)
