#! /usr/bin/python3
from sqlalchemy.sql.functions import rank
import ts3
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import exc
import crud, modelsdb, schemas
from database import *
import time
import FunctionUpdateCurrentParameters
import multiprocessing
import threading
import logging
import function
import sched
import config
import logging
import requests
import signal
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

url = config.influx_db['url']
token = config.influx_db['token']
org = config.influx_db['org']
bucket = config.influx_db['bucket']

proxy_api = config.proxy['api']

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

send_to_influx = client.write_api(write_options=SYNCHRONOUS)
logger = logging.getLogger('SYSTEM WATCHER  || V-A-A-8')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

s = sched.scheduler(time.time, time.sleep)
modelsdb.Base.metadata.create_all(bind=engine)
to_delete={}
list_is_online=[]
admin_list_online_CLID=[]
list_notice_user=[]

# test
def convert_list_to_string(input):
    output=""
    for element in input:
        output += element
    return output


def querry_list_CLID_online_now(ts3conn):
    list=ts3conn.clientlist()
    response=[]
    for i in list.parsed:
        try:
            info_client=ts3conn.clientinfo(clid=i['clid'])
            if info_client[0]['client_type']=='0':
                response.append(int(i['clid']))
        except: pass
    return response


def check_to_remove_ban(ts3conn):
    ts3conn = ts3conn
    db_connection = SessionLocal()
    current_time = int(time.time())
    ban_history = crud.get_ban_history_active(db_connection)
    for ban in ban_history:
        if ban.time_to <= current_time:
            action = crud.get_action_by_id(db, ban.action_id)
            ban_this_same_action_user = crud.get_ban_history_active_by_action_id(db, ban.action_id, ban.ban_client_dbid)
            if len(ban_this_same_action_user) <= 1:
                if action.action == 'add_server_group':
                    try:
                        ts3conn.servergroupdelclient(sgid=action.group_id, cldbid=ban.ban_client_dbid)
                        logger.info('Rank id: %s was deleted', action.group_id)
                    except: pass
            crud.update_delete_ban_history(db_connection, ban.id, current_time)
            logger.info('Ban id: %s was deleted', ban.id)

    db.close()
    s.enter(60, 10, check_to_remove_ban, (ts3conn,))


def upadate_client_on_ts(ts3conn):

    ts3conn=ts3conn
    db=SessionLocal()
    list_CLID=querry_list_CLID_online_now(ts3conn)
    host_info = ts3conn.serverinfo()

    if crud.querry_status_modules(db, "update_client_on_ts"):
        parameters = crud.querry_dictionary(db, "DESC_SERVER").desc
        if parameters:
            parameters = parameters.replace("%%CLIENTS_AMOUNT%%", str(len(list_CLID)))
            ifno_server = ts3conn.serverinfo()
            if not ifno_server[0]['virtualserver_name'] == parameters:
                ts3conn.serveredit(virtualserver_name=parameters)
                data = date()
                logger.debug('Set new serwer: desc || %s', parameters)

    p = influxdb_client.Point("online_on_ts").field("current_user_online", int(len(list_CLID)))
    send_to_influx.write(bucket=bucket, org=org, record=p)

    p1 = influxdb_client.Point("online_on_ts").field("current_ping", float(host_info[0]['virtualserver_total_ping']))
    send_to_influx.write(bucket=bucket, org=org, record=p1)

    p2 = influxdb_client.Point("online_on_ts").field("current_packet_loss", (float(host_info[0]['virtualserver_total_packetloss_total'])*100))
    send_to_influx.write(bucket=bucket, org=org, record=p2)
    db.close()
    s.enter(1, 1, upadate_client_on_ts, (ts3conn,))


def update_current_parameters_user(ts3connect):
    logger.debug('Run update current parameters user')
    list_clid = querry_list_CLID_online_now(ts3conn)
    for element in list_clid:
        try:
            info_client = ts3conn.clientinfo(clid=str(element))
            FunctionUpdateCurrentParameters.update_nick(info_client)
        except:
            pass
    logger.debug('Finish update current parameters user')
    s.enter(5, 6, update_current_parameters_user, (ts3conn,))


def update_and_notice_user(ts3connect):
    global to_delete
    global list_is_online
    db = SessionLocal()
    list_CLID = querry_list_CLID_online_now(ts3connect)
    list_DBID = []
    for i in list_CLID:
        try:
            info_client = ts3connect.clientinfo(clid=str(i))
            list_DBID.append(int(info_client[0]['client_database_id']))
        except: pass
    # check list
    temp_list = list(map(str, list_DBID))
    temp_list = ','.join(temp_list)
    crud.update_current_online(db, temp_list)
    if not list_is_online:#iniclailzacja listy
        for DBID in list_DBID:
            CLID = convert_DBID_to_CLID(ts3connect, DBID)
            try:
                info_client = ts3connect.clientinfo(clid=str(CLID))
                if int(info_client[0]['connection_connected_time'])>60000:  #niż minutę
                    list_is_online.append(DBID)
                else:
                    logger.info('User Id: %s connect Ts3', DBID)
                    list_is_online.append(DBID)
                    crud.upadate_base_users(db, info_client)
                    check_ip_proxy(db, info_client)
                    # during ini
                    if crud.querry_status_modules(db, "send_hello_mesage_to_client"):
                        send_message_to_user(ts3connect, info_client,str(len(list_CLID)))
            except: pass
        logger.info('List on-line ini || status: OK')
    else:
        for DBID in list_DBID:

            if not check_item_in_list(DBID, list_is_online):
                try:
                    to_delete[DBID]
                except:
                    list_is_online.append(DBID)
                    logger.info('User Id: %s connect Ts3', DBID)
                    CLID = convert_DBID_to_CLID(ts3connect, DBID)
                    try:
                        info_client = ts3connect.clientinfo(clid=str(CLID))
                        crud.upadate_base_users(db, info_client)
                        check_ip_proxy(db, info_client)
                        if crud.querry_status_modules(db, "send_hello_mesage_to_client"):
                            send_message_to_user(ts3connect, info_client, str(len(list_CLID)))
                    except exc.IntegrityError:
                        logger.error('User DBID: %s, UID: %s', DBID, info_client[0]['client_unique_identifier'])
                    except: pass
                else:
                    del to_delete[DBID]
                    list_is_online.append(DBID)
                    logger.info('User Id: %s re-connect Ts3', DBID)

        for DBID in list_is_online:
            if not check_item_in_list(DBID,list_DBID):
                logger.info('User Id: %s leave Ts3', DBID)
                to_delete[DBID] = 0
                list_is_online.remove(DBID)
                

    db.close()
    s.enter(2, 2, update_and_notice_user, (ts3connect,))


def check_ip_proxy(db, clientinfo):
    if not crud.check_ip_record(db, clientinfo[0]['connection_client_ip']):
        response = requests.get("https://proxycheck.io/v2/" + clientinfo[0]['connection_client_ip'] +
                            "?key=" + proxy_api + "&vpn=1&asn=1&risk=2&port=1&seen=1")
        response = response.json()
        if response['status'] == 'ok':
            crud.add_check_ip(db, clientinfo[0]['connection_client_ip'], response[clientinfo[0]['connection_client_ip']])
            logger.debug('Checked %s ip and add to list', clientinfo[0]['connection_client_ip'])


def chceck_to_del():
    db = SessionLocal()
    interval_to_del = int(crud.return_settings(db, "interval_to_del"))
    global to_delete
    if to_delete:
        try:
            for key in to_delete:
                if to_delete[key] >= interval_to_del:
                    logger.info('User Id: %s disconnect from Ts3', key)
                    del to_delete[key]
                else:
                    to_delete[key] = to_delete[key]+1
        except: pass
    db.close()
    s.enter(60, 3, chceck_to_del)


def send_message_to_user(ts3conn, info_client, number_client):
    db = SessionLocal()
    DBID = int(info_client[0]['client_database_id'])
    CLID = convert_DBID_to_CLID(ts3conn,DBID)
    number_lines = int(crud.return_settings(db,"send_hello_mesage_index"))
    if number_lines != 0:
        lines = crud.querry_dictionary_sort_id(db, "MESSAGE_TO_USER")
        for i in range (0, number_lines):
            message=lines[i].desc
            if "%%NICK%%" in message:
                message = message.replace("%%NICK%%", info_client[0]['client_nickname'])
            if "%%NUMBER_USER%%" in message:
                message = message.replace("%%NUMBER_USER%%", number_client)
            if "%%FIRST_DATE%%" in message:                
                message = message.replace("%%FIRST_DATE%%", datetime.utcfromtimestamp(int(info_client[0]['client_created'])).strftime('%Y-%m-%d %H:%M:%S'))
            if "%%CONECTCION_AMOUNT%%" in message:
                message = message.replace("%%CONECTCION_AMOUNT%%", info_client[0]['client_totalconnections'])
            try:
                ts3conn.sendtextmessage(targetmode=1, target=CLID, msg=message)
            except: pass
    db.close()


def check_item_in_list(item, list_to_check):
    if list_to_check:
        for i in list_to_check:
            if item==i:
                return True
    return False


def convert_DBID_to_CLID(ts3conn, DBID):
    try:
        user_info = ts3conn.clientdbinfo(cldbid=DBID)
        CLID = ts3conn.clientgetids(cluid=user_info[0]['client_unique_identifier'])
        CLID = CLID[0]['clid']
    except: return 0
    return int(CLID)

def update_admin_list(ts3connection):
    global admin_list_online_CLID
    ts3connection = ts3conn

    db = SessionLocal()
    channel_number =crud.return_settings(db, "ADMIN_LIST_NUMBER")
    channel_name = crud.querry_dictionary(db, "CHANNEL_ADMIN_NAME").desc
    rank_id_list = crud.return_admin_rank_id(db)
    list_admin_DBID=[]
    for i in rank_id_list:
        list_DBID = crud.return_DBID_privilage_by_rank_id(db, i.rank_id)
        temp_nick_list=[]
        for x in list_DBID:
            temp_nick_list.append(crud.return_nick_by_DBID(db, x.DBID))
        temp_nick_list.sort()
        for y in temp_nick_list:
            list_admin_DBID.append(crud.return_DBID_by_nick(db, y))
    # CHECK DBID LIST
    list_CLID = []
    if list_admin_DBID:

        for i in list_admin_DBID:
            CLID = convert_DBID_to_CLID(ts3conn, int(i))
            if not CLID == 0:
                list_CLID.append(CLID)
    admin_list_online_CLID = list_CLID
    channel_name = channel_name.replace("%%ADMIN_ONLINE%%", str(len(list_CLID)))
    channel = ts3conn.channelinfo(cid=channel_number)
    if not channel[0]['channel_name'] == channel_name:
        ts3conn.channeledit(cid=channel_number, channel_name=channel_name)
    if not len(list_CLID)==0:
        header = crud.querry_dictionary(db, "HEAD_ADMIN_LIST").desc
        header = header.replace("\\n", '\n')
        admin_URI_list = []
        separator = crud.querry_dictionary(db, "ADMIN_LIST_SEPARATOR").desc
        style = crud.querry_dictionary(db, "ADMIN_LIST_STYLE").desc
        for i in list_CLID:
            try:
                client_info = ts3conn.clientinfo(clid=str(i))
            except: pass
            else:
                admin_URI_list.append("\n"+separator+"[URL=client://0/"+client_info[0]['client_unique_identifier']+"]"+client_info[0]['client_nickname']+"[/URL]")
        list_online = (''.join(admin_URI_list))
        description = header + style.replace("%%CONTENT%%", list_online)
        if not channel[0]['channel_description'] == description:
            ts3conn.channeledit(cid=channel_number, channel_description=str(description))
    else:
        header = crud.querry_dictionary(db, "HEAD_ADMIN_LIST_OFFLINE").desc
        header = header.replace("\\n", '\n')
        if not channel[0]['channel_description'] == header:
            ts3conn.channeledit(cid=channel_number,channel_description=str(header))
    db.close()
    s.enter(5, 4, update_admin_list, (ts3conn,))


def notification_admin(ts3connect):
    global admin_list_online_CLID
    # admin_list_online_clid = admin_list_online_CLID
    global list_notice_user
    poke_message = crud.querry_dictionary(db, "HELP_MESSAGE_POKE_TO_ADMIN").desc
    message_to_client_admin_offline = crud.querry_dictionary(db, "MESSAGE_TO_USER_ADMIN_OFF_LINE").desc
    message_to_client_admin_online = crud.querry_dictionary(db, "MESSAGE_TO_USER_ADMIN_ON_LINE").desc
    ts3connection = ts3connect

    channel_number = crud.return_settings(db, "HELP_CHANNEL_LIST_NUMBER")
    channel = ts3connection.channelinfo(cid=channel_number)
    if channel[0]['seconds_empty'] == '-1':
        admin_on_channel = False
        for i in admin_list_online_CLID:
            try:
                admin_info = ts3connection.clientinfo(clid=i)
                if admin_info[0]['cid'] == str(channel_number):
                    admin_on_channel = True
            except:
                pass
        if not admin_on_channel:
            # not admin on channel
            list_user_on_help_channel = []
            list_clid = ts3connection.clientlist()
            for i in list_clid:
                if i['cid'] == str(channel_number):
                    list_user_on_help_channel.append(i['clid'])
            for i in list_user_on_help_channel:
                if not i in list_notice_user:
                    nick = ''
                    for x in list_clid:
                        if x['clid'] == i:
                            nick = x['client_nickname']
                    if admin_list_online_CLID:
                        # admin is online
                        message = message_to_client_admin_online
                    else:
                        # not admin online
                        message = message_to_client_admin_offline
                    message = message.replace('%%NICK%%', nick)
                    try:
                        ts3connection.sendtextmessage(targetmode=1, target=i, msg=message)
                    except: pass
                    if not list_notice_user:
                        # first poke
                        poke_message = poke_message.replace("%%VALUE_USER%%", str(len(list_user_on_help_channel)))
                        for x in admin_list_online_CLID:
                            try:
                                ts3connection.clientpoke(msg=poke_message, clid=str(x))
                            except: pass
                        poke_interval = int(crud.return_settings(db, "INTERVAL_TO_POKE"))
                        s.enter(poke_interval, 5, poke_admin, (ts3connection,))
                    list_notice_user.append(i)
                for x in list_notice_user:
                    if not x in list_user_on_help_channel:
                        list_notice_user.remove(x)

    else:
        list_notice_user = []

    s.enter(10, 4, notification_admin, (ts3connection,))


def poke_admin(ts3connect):
    ts3connection = ts3connect
    global list_notice_user
    poke_interval = int(crud.return_settings(db, "INTERVAL_TO_POKE"))
    channel_number = crud.return_settings(db, "HELP_CHANNEL_LIST_NUMBER")
    channel = ts3connection.channelinfo(cid=channel_number)
    if channel[0]['seconds_empty'] == '-1':
        poke_message = crud.querry_dictionary(db, "HELP_MESSAGE_POKE_TO_ADMIN").desc
        poke_message = poke_message.replace("%%VALUE_USER%%", str(len(list_notice_user)))
        admin_on_channel = False
        for i in admin_list_online_CLID:
            try:
                admin_info = ts3connection.clientinfo(clid=i)
                if admin_info[0]['cid'] == str(channel_number):
                    admin_on_channel = True
            except:
                pass
        if not admin_on_channel:
            for x in admin_list_online_CLID:
                ts3connection.clientpoke(msg=poke_message, clid=str(x))
        s.enter(poke_interval, 5, poke_admin, (ts3connection,))


def list_on_line(ts3conn):
    now = datetime.now()
    logger.debug('UPDATE ON-LINE STARTED')
    db = SessionLocal()
    db.query(modelsdb.online_users_on_teamsepak).delete()
    db.execute("ALTER TABLE online_users_on_teamsepak AUTO_INCREMENT=1")
    db.commit()
    list = ts3conn.clientlist()
    k = 0
    for i in list.parsed:
        try:
            info_client = ts3conn.clientinfo(clid=i['clid'])
            k = k+1
            if info_client[0]['client_type'] == '0' and \
                    not crud.return_user_by_DBID(db, info_client[0]['client_database_id']):
                crud.add_online_users_on_teamsepak(db, info_client[0]['client_database_id'],
                                                   info_client[0]['client_unique_identifier'],
                                                   info_client[0]['connection_client_ip'],
                                                   info_client[0]['client_nickname'])
        except: pass
    db.commit()
    now = datetime.now()
    logger.debug('UPDATE ON-LINE FINISHED || INSERT: %s ROW', k)
    db.close()


def update_time_on_line(ts3conn):
    now = datetime.now()
    logger.debug('UPDATE TIME USER ON-LINE STARTED')
    db = SessionLocal()
    list = ts3conn.clientlist()
    k = 0
    for i in list.parsed:
        try:
            info_client = ts3conn.clientinfo(clid=i['clid'])
            if info_client[0]['client_type']=='0':
                DBID = info_client[0]['client_database_id']
                user = crud.get_user_from_timing_by_dbid(db,DBID)
                if user:
                    if info_client[0]['client_input_hardware']=='0':
                        crud.upadte_online_timing_disabled_users(db,DBID)
                    if info_client[0]['client_away']=='0':
                        # nioe jest awar
                        if int(info_client[0]['client_idle_time'])>60000:
                            crud.upadte_idle_timing_online_users(db,DBID)
                        else:
                            crud.upadte_online_timing_online_users(db,DBID)
                            # warunek dla disabled
                    else:
                        # jest away
                        crud.upadte_away_timing_online_users(db,DBID)
                else:
                    crud.add_timing_online_users(db,DBID)
                db.commit()
        except: pass
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    db.close()
    logger.debug('UPDATE TIME USER ON-LINE FINISHED || INSERT: %s ROWs', k)


def end_session(ts3conn):
        ts3conn.logout()
        ts3conn.quit()


def date():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


if __name__ == "__main__":
    db = SessionLocal()
    status_list = crud.querry_status_modules_all(db)
    with ts3.query.TS3Connection(config.query_ts3['host'], config.query_ts3['port']) as ts3conn:

        ts3conn.login(client_login_name=config.query_ts3['login'], client_login_password=config.query_ts3['pass'])
        ts3conn.use(sid=1)
        try:
            ts3conn.clientupdate(client_nickname="Sauron TS3")
        except:
            pass
        logger.info('SYSTEM START || status: OK')
        db.close()
        for i in status_list:
            if i.module_name == "update_client_on_ts":
                logger.info('Update client ini || status: OK')
                s.enter(1, 1, upadate_client_on_ts, (ts3conn,))                
            if i.module_name == "update_admin_list_on_ts":
                logger.info('List admin ini || status: OK')
                s.enter(5, 4, update_admin_list, (ts3conn,))
            if i.module_name == "poke_admin":
                logger.info('notification admin ini || status: OK')
                s.enter(10, 5, notification_admin, (ts3conn,))
            if i.module_name == "update_current_client_para":
                logger.info('Watch current user parameters ini || status: O')
                s.enter(5, 6, update_current_parameters_user, (ts3conn,))
        s.enter(2, 2, update_and_notice_user, (ts3conn,))
        s.enter(60, 3, chceck_to_del)
        s.enter(1, 10, check_to_remove_ban, (ts3conn,))
        s.run()



