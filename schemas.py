#! /usr/bin/python3
from typing import List, Optional, Dict, Optional, Tuple

from pydantic import BaseModel
class dataIp(BaseModel):
    ip: str
    asn: str
    provider: str
    continent: str
    country: str
    city: str
    region: str
    region_code: str
    latitude: str
    longitude: str
    iso_code: str
    proxy: str
    type: str
    port: str
    risk: str
    attack_history: str
    last_seen_human: str
    last_seen_unix: str
#class UserOnline(BaseModel):
#    DBID: int
#    UID: str
#    IP: str
#    Nick: str


