import crud
from sqlalchemy.orm import Session
from database import *
import function
import requests
import config

proxy_api = config.proxy['api']


def update_nick(data_client):
    db = SessionLocal()
    crud.update_current_nick(db, int(data_client[0]['client_database_id']), data_client[0]['client_nickname'])
    ip_record = crud.return_ip_record(db, data_client[0]['connection_client_ip'])
    if not ip_record:
        response = requests.get("https://proxycheck.io/v2/" + data_client[0]['connection_client_ip'] +
                                "?key=" + proxy_api + "&vpn=1&asn=1&risk=2&port=1&seen=1")
        response = response.json()
        if response['status'] == 'ok':
            crud.add_check_ip(db, data_client[0]['connection_client_ip'],
                              response[data_client[0]['connection_client_ip']])
    ip_record = crud.return_ip_record(db, data_client[0]['connection_client_ip'])
    if ip_record:
        crud.update_current_ip(db, int(data_client[0]['client_database_id']), ip_record.id, data_client[0]['connection_client_ip'])
    db.close()

