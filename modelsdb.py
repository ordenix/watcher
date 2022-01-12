#! /usr/bin/python3
from sqlalchemy import *
# from sqlalchemy.orm import relationship

from database import *


class UserRegister(Base):
    __tablename__ = "users_register"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(32))
    password = Column(String(64))
    is_banned = Column(Boolean, default=False)
    date_created = Column(Integer)
    last_login = Column(Integer)
    uid = Column(String(32), unique=True)
    dbid = Column(Integer, unique=True)
    role = Column(String(32))


class PrivilegeToRank(Base):
    __tablename__ = "privilage_to_rank"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, ForeignKey("users_register.dbid"))
    rank_id = Column(Integer, ForeignKey("grant_rank.rank_id"))


class GrantRank(Base):
    __tablename__ = "grant_rank"
    id = Column(Integer, primary_key=True, index=True)
    rank_id = Column(Integer, unique=True)
    rank_name = Column(String(32))
    group_id = Column(Integer)
    acces_to_register = Column(Boolean)
    acces_to_grant_rank = Column(Boolean)
    acces_to_staff_user = Column(Boolean)


class BaseUsersOnTeamsepak(Base):
    __tablename__ = "base_users_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    UID = Column(String(32), unique=True)
    IP = Column(Text)
    Nick = Column(Text(convert_unicode=True))


class BaseUsersInfoOnTeamsepak(Base):
    __tablename__ = "base_users_info_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    total_connections = Column(Integer)
    real_total_connections = Column(Integer)
    created = Column(Integer)
    last_connect = Column(Integer)
    myteamspeak_id = Column(String(128))
    description = Column(Text(convert_unicode=True))


class BaseUsersMiscOnTeamsepak(Base):
    __tablename__ = "base_users_misc_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    client_badges = Column(String(128))
    client_country = Column(String(128))
    client_version = Column(String(128))
    platform = Column(String(128))


class BaseUsersServerDataOnTeamsepak(Base):
    __tablename__ = "base_users_server_data_on_teamsepak"
    id = Column(Integer, primary_key=True, index=True)
    DBID = Column(Integer, unique=True)
    server_groups = Column(String(128))
    is_register = Column(Boolean) 
    check_rules = Column(Boolean)


class DictionaryBot(Base):
    __tablename__ = "dictionary_bot"
    id = Column(Integer, primary_key=True, index=True)
    parameters = Column(String(32))
    desc = Column(String(128))
    sort_id = Column(Integer)


class ActiveModules(Base):
    __tablename__ = "active_modules"
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(32))
    status = Column(Boolean)


class ModulesSettings(Base):
    __tablename__ = "modules_settings"
    id = Column(Integer, primary_key=True, index=True)
    setting = Column(String(32))
    options = Column(String(32))


class CheckedIP(Base):
    __tablename__ = "CheckedIP"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(128))
    asn = Column(String(128))
    provider = Column(String(128))
    continent = Column(String(128))
    country = Column(String(128))
    city = Column(String(128))
    region = Column(String(128))
    region_code = Column(String(128))
    latitude = Column(String(128))
    longitude = Column(String(128))
    iso_code = Column(String(128))
    proxy = Column(String(128))
    type = Column(String(128))
    port = Column(String(128))
    risk = Column(String(128))
    attack_history = Column(String(128))
    last_seen_human = Column(String(128))
    last_seen_unix = Column(String(128))


class IpHistory(Base):
    __tablename__ = "IpHistory"
    id = Column(Integer, primary_key=True, index=True)
    id_ip = Column(Integer)
    dbid = Column(Integer)
    time = Column(Integer)


class NickHistory(Base):
    __tablename__ = "NickHistory"
    id = Column(Integer, primary_key=True, index=True)
    Nick = Column(Text(convert_unicode=True))
    dbid = Column(Integer)
    time = Column(Integer)


class OnlineUserOnTs(Base):
    __tablename__ = "OnlineUserOnTs"
    id = Column(Integer, primary_key=True, index=True)
    list = Column(String(256))


class BanHistoryTable(Base):
    __tablename__ = "ban_history_table"
    id = Column(Integer, primary_key=True, index=True)
    ban_client_dbid = Column(Integer)
    ban_id = Column(Integer)
    action_id = Column(Integer)
    additional_info = Column(String(1024))
    add_admin_dbid = Column(Integer)
    time_add = Column(Integer)
    time_to = Column(Integer)
    active = Column(Boolean)
    time_to_overflow = Column(Integer)
    to_commit = Column(Boolean)
    commit = Column(Boolean)
    commit_admin_dbid = Column(Integer)
    time_commit = Column(Integer)
    auto_ban = Column(Boolean)
    removed = Column(Boolean)
    removed_dbid = Column(Integer)
    time_removed = Column(Integer)


class ActionBanType(Base):
    __tablename__ = "ActionBanType"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    group_id = Column(Integer)
    action = Column(String(256))
    time = Column(Boolean)
