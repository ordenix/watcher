#! /usr/bin/python3
from sqlalchemy.orm import Session
from sqlalchemy import desc,asc
from datetime import datetime
import modelsdb, schemas



#def query_header_admin_list(db: Session):
def querry_dictionary(db: Session,parameters):
    querry = db.query(modelsdb.DictionaryBot).filter(modelsdb.DictionaryBot.parameters == parameters).first()
    if not querry:
        return None
    return querry
def querry_dictionary_sort_id(db: Session,parameters):
    querry = db.query(modelsdb.DictionaryBot).filter(modelsdb.DictionaryBot.parameters == parameters).order_by(modelsdb.DictionaryBot.sort_id.asc()).all()
    if not querry:
        return None
    return querry
def querry_status_modules(db: Session,module):
    querry = db.query(modelsdb.ActiveModules).filter(modelsdb.ActiveModules.module_name == module).first()
    if not querry:
        return False
    return querry.status
def querry_status_modules_all(db: Session):
    querry = db.query(modelsdb.ActiveModules).all()
    if not querry:
        return False
    return querry
def upadate_base_users(db: Session,info_client):
    querry = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.DBID == int(info_client[0]['client_database_id'])).first()
    if querry:
        on_db_user = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.DBID == int(info_client[0]['client_database_id'])).first()
        info_db_user = db.query(modelsdb.BaseUsersInfoOnTeamsepak).filter(modelsdb.BaseUsersInfoOnTeamsepak.DBID == int(info_client[0]['client_database_id'])).first()
        misc_db_user = db.query(modelsdb.BaseUsersMiscOnTeamsepak).filter(modelsdb.BaseUsersMiscOnTeamsepak.DBID == int(info_client[0]['client_database_id'])).first()
        server_data_db_user = db.query(modelsdb.BaseUsersServerDataOnTeamsepak).filter(modelsdb.BaseUsersServerDataOnTeamsepak.DBID == int(info_client[0]['client_database_id'])).first()
        
        on_db_user.IP=info_client[0]['connection_client_ip']
        on_db_user.Nick=info_client[0]['client_nickname']

        info_db_user.total_connections=int(info_client[0]['client_totalconnections'])
        info_db_user.real_total_connections +=1
        info_db_user.last_connect=int(info_client[0]['client_lastconnected'])
        info_db_user.myteamspeak_id=info_client[0]['client_myteamspeak_id']
        info_db_user.description=info_client[0]['client_description']

        misc_db_user.client_badges=info_client[0]['client_badges']
        misc_db_user.client_country=info_client[0]['client_country']
        misc_db_user.client_version=info_client[0]['client_version']
        misc_db_user.platform=info_client[0]['client_platform']

        server_data_db_user.server_groups=info_client[0]['client_servergroups']

        db.add(on_db_user)
        db.add(info_db_user)
        db.add(misc_db_user)
        db.add(server_data_db_user)
        db.commit()
        db.refresh(on_db_user)
        db.refresh(info_db_user)
        db.refresh(misc_db_user)
        db.refresh(server_data_db_user)

    else: #nie ma
        on_db_user = modelsdb.BaseUsersOnTeamsepak(DBID=int(info_client[0]['client_database_id']), UID=info_client[0]['client_unique_identifier'], IP=info_client[0]['connection_client_ip'], Nick=info_client[0]['client_nickname'])
        info_db_user = modelsdb.BaseUsersInfoOnTeamsepak(DBID=int(info_client[0]['client_database_id']), total_connections=int(info_client[0]['client_totalconnections']), real_total_connections=0, created=int(info_client[0]['client_created']), last_connect=int(info_client[0]['client_lastconnected']), myteamspeak_id=info_client[0]['client_myteamspeak_id'], description=info_client[0]['client_description'])
        misc_db_user = modelsdb.BaseUsersMiscOnTeamsepak(DBID=int(info_client[0]['client_database_id']), client_badges=info_client[0]['client_badges'], client_country=info_client[0]['client_country'], client_version=info_client[0]['client_version'], platform=info_client[0]['client_platform'])
        server_data_db_user = modelsdb.BaseUsersServerDataOnTeamsepak(DBID=int(info_client[0]['client_database_id']), server_groups=info_client[0]['client_servergroups'])
        db.add(on_db_user)
        db.add(info_db_user)
        db.add(misc_db_user)
        db.add(server_data_db_user)
        db.commit()
        db.refresh(on_db_user)
        db.refresh(info_db_user)
        db.refresh(misc_db_user)
        db.refresh(server_data_db_user)

def return_settings(db: Session,setting):
    querry = db.query(modelsdb.ModulesSettings).filter(modelsdb.ModulesSettings.setting == setting).first()
    if not querry:
        return None
    return querry.options
def return_admin_rank_id(db: Session):
    query = db.query(modelsdb.GrantRank).all()
    return query
def return_DBID_privilage_by_rank_id(db: Session,rank_id):
    query = db.query(modelsdb.PrivilegeToRank).filter(modelsdb.PrivilegeToRank.rank_id == rank_id).all()
    return query
def return_nick_by_DBID(db: Session,DBID):
    query = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.DBID == DBID).first()
    return query.Nick
def return_DBID_by_nick(db: Session,Nick):
    query = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.Nick == Nick).first()
    return query.DBID

def add_online_users_on_teamsepak(db: Session, DBID, UID, IP, Nick):
    db_user = modelsdb.online_users_on_teamsepak(DBID=DBID, UID=UID, IP=IP, Nick=Nick)
  #  db.create(modelsdb.online_users_on_teamsepak,checkfirst=True)
    db.add(db_user)
    db.commit()
    #db.refresh(db_user)
    return
def return_online_users_on_teamsepak(db: Session):
    return db.query(modelsdb.online_users_on_teamsepak).all()
def return_user_by_DBID(db,DBID):
    return db.query(modelsdb.online_users_on_teamsepak).filter(modelsdb.online_users_on_teamsepak.DBID==DBID).first()
def get_user_from_timing_by_dbid(db: Session, DBID):
    return db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
def add_timing_online_users(db: Session, DBID):
    db_user = modelsdb.time_users_on_teamsepak(DBID=DBID, TIME_TOTAL=0,TIME_ONLINE=0,TIME_AWAY=0,TIME_IDLE=0,TIME_MIC_DISABLED=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return
def upadte_away_timing_online_users(db: Session, DBID):
    user = db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
    user.TIME_TOTAL +=1
    user.TIME_AWAY +=1
    db.commit()
def upadte_idle_timing_online_users(db: Session, DBID):
    user = db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
    user.TIME_TOTAL +=1
    user.TIME_IDLE +=1
    db.commit()
def upadte_online_timing_online_users(db: Session, DBID):
    user = db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
    user.TIME_TOTAL +=1
    user.TIME_ONLINE +=1
    db.commit()
def upadte_online_timing_disabled_users(db: Session, DBID):
    user = db.query(modelsdb.time_users_on_teamsepak).filter(modelsdb.time_users_on_teamsepak.DBID==DBID).first()
    user.TIME_MIC_DISABLED +=1
    db.commit()


def check_ip_record(db: Session, ip):
    record = db.query(modelsdb.CheckedIP).filter(modelsdb.CheckedIP.ip == ip).first()
    if record:
        return True
    else:
        return False


def return_ip_record(db: Session, ip):
    record = db.query(modelsdb.CheckedIP).filter(modelsdb.CheckedIP.ip == ip).first()
    return record


def add_check_ip(db: Session, ip, response):
    data = schemas.dataIp(ip=ip, asn='', provider='', continent='', country='', city='', region='', region_code='',
                          latitude='', longitude='', iso_code='',  proxy='', type='', port='', risk='',
                          attack_history='', last_seen_human='', last_seen_unix='')
    try:
        if response['asn']:
            data.asn = response['asn']
    except: pass
    try:
        if response['provider']:
            data.provider = response['provider']
    except: pass
    try:
        if response['continent']:
            data.continent = response['continent']
    except: pass
    try:
        if response['country']:
            data.country = response['country']
    except: pass
    try:
        if response['city']:
            data.city = response['city']
    except: pass
    try:
        if response['region']:
            data.region = response['region']
    except: pass
    try:
        if response['region_code']:
            data.region_code = response['region_code']
    except: pass
    try:
        if response['latitude']:
            data.latitude = response['latitude']
    except: pass
    try:
        if response['longitude']:
            data.longitude = response['longitude']
    except: pass
    try:
        if response['iso_code']:
            data.iso_code = response['iso_code']
    except: pass
    try:
        if response['proxy']:
            data.proxy = response['proxy']
    except: pass
    try:
        if response['type']:
            data.type = response['type']
    except: pass
    try:
        if response['port']:
            data.port = response['port']
    except: pass
    try:
        if response['risk']:
            data.risk = response['risk']
    except: pass
    try:
        if response['attack_history']:
            data.attack_history = response['attack_history']
    except: pass
    try:
        if response['last_seen_human']:
            data.last_seen_human = response['last_seen_human']
    except: pass
    try:
        if response['last_seen_unix']:
            data.last_seen_unix = response['last_seen_unix']
    except: pass
    record = modelsdb.CheckedIP(ip=data.ip, asn=data.asn, provider=data.provider, continent=data.continent,
                                country=data.country, city=data.city, region=data.region, region_code=data.region_code,
                                latitude=data.latitude, longitude=data.longitude, iso_code=data.iso_code,
                                proxy=data.proxy, type=data.type, port=data.port, risk=data.risk,
                                attack_history=data.attack_history, last_seen_human=data.last_seen_human,
                                last_seen_unix=data.last_seen_unix)
    db.add(record)
    db.commit()


def update_current_nick(db: Session, dbid: int, nick: str):
    record = db.query(modelsdb.NickHistory).filter(modelsdb.NickHistory.dbid == dbid).order_by(modelsdb.NickHistory.id.desc()).first()
    record2 = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.DBID == dbid).first()
    time = int(datetime.now().timestamp())
    if record:
        if record.Nick != nick:
            record = modelsdb.NickHistory(Nick=nick, dbid=dbid, time=time)
            if record2:
                record2.Nick = nick
            db.add(record)
            db.commit()
    else:
        record = modelsdb.NickHistory(Nick=nick, dbid=dbid, time=time)
        db.add(record)
        db.commit()


def update_current_ip(db: Session, dbid: int, id_ip: int, ip: str):
    record = db.query(modelsdb.IpHistory).filter(modelsdb.IpHistory.dbid == dbid).order_by(modelsdb.IpHistory.id.desc()).first()
    record2 = db.query(modelsdb.BaseUsersOnTeamsepak).filter(modelsdb.BaseUsersOnTeamsepak.DBID == dbid).first()
    time = int(datetime.now().timestamp())
    if record:
        if record.id_ip != id_ip:
            record = modelsdb.IpHistory(id_ip=id_ip, dbid=dbid, time=time)
            if record2:
                record2.IP = ip
            db.add(record)
            db.commit()
    else:
        record = modelsdb.IpHistory(id_ip=id_ip, dbid=dbid, time=time)
        db.add(record)
        db.commit()


def update_current_online(db: Session, user_list: list):
    record = db.query(modelsdb.OnlineUserOnTs).filter(modelsdb.OnlineUserOnTs.id == 1).first()
    if record:
        record.list = user_list
    else:
        record = modelsdb.OnlineUserOnTs(list=user_list, id=1)
        db.add(record)
    db.commit()


def get_ban_history_active(db: Session):
    return db.query(modelsdb.BanHistoryTable).filter(modelsdb.BanHistoryTable.active == 1).all()


def get_ban_history_active_by_action_id(db: Session, action_id: int, dbid: int):
    return db.query(modelsdb.BanHistoryTable).filter(modelsdb.BanHistoryTable.active == 1).\
           filter(modelsdb.BanHistoryTable.action_id == action_id).\
           filter(modelsdb.BanHistoryTable.ban_client_dbid == dbid).all()


def get_action_by_id(db: Session, action_id: int):
    return db.query(modelsdb.ActionBanType).filter(modelsdb.ActionBanType.id == action_id).first()


def update_delete_ban_history(db: Session, ban_id: int, time: int):
    record = db.query(modelsdb.BanHistoryTable).filter(modelsdb.BanHistoryTable.id == ban_id).first()
    record.active = 0
    record.removed = 1
    record.removed_dbid = -1
    record.time_removed = time
    db.commit()
