import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

# TODO: Store the database connection string in a config file
engine = create_engine("sqlite:///db.sqlite")
Session = sessionmaker(bind=engine)
session = scoped_session(Session)

Base = declarative_base()
Base.query = session.query_property()

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    ip_address = Column(String)
    port = Column(Integer)

    def __init__(self, name, description, ip_address, port):
        self.name = name
        self.description = description
        self.ip_address = ip_address
        self.port = port

    def __repr__(self):
        return "<Client id:{0}, name:{1}, ip_address:{2}, port:{3}>".format(self.id, self.name,
                                                                            self.ip_address, self.port)


class ClientGroup(Base):
    __tablename__ = "client_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<ClientGroup id:{0}, name:{1}>".format(self.id, self.name)


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    version = Column(Float)

    def __init__(self, name, description, version):
        self.name = name
        self.description = description
        self.version = version

    def __repr__(self):
        return "<Plugin id:{0}, name:{1}, version:{2}>".format(self.id, self.name, self.version)


class PluginResult(Base):
    __tablename__ = "plugin_results"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship("Plugin")
    alert_level = Column(Integer)
    message = Column(Text)
    value = Column(Float)
    captured_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, plugin_id, alert_level, message, value):
        self.plugin_id = plugin_id
        self.alert_level = alert_level
        self.message = message
        self.value = value

    def __repr__(self):
        return "<PluginResult id:{0}, plugin_id:{1}, alert_level:{2}>".format(  self.id, self.plugin_id,
                                                                                self.alert_level)


class PluginAssignment(Base):
    __tablename__ = "plugin_assignments"

    id = Column(Integer, primary_key=True)
    member_client_id = Column(Integer, ForeignKey(Client.id))
    member_client = relationship("Client")
    member_group_id = Column(Integer, ForeignKey(ClientGroup.id))
    member_group = relationship("ClientGroup")
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship("Plugin")

    def __init__(self, member_client_id, member_group_id, plugin_id):
        self.member_client_id = member_client_id
        self.member_group_id = member_group_id
        self.plugin_id = plugin_id

    def __repr__(self):
        return "<PluginAssignment id:{0}, member_client_id:{1}, member_group_id:{2}, plugin_id:{3}>".format(
                                    self.id, self.member_client_id, self.member_group_id, self.plugin_id)


class GroupAssignment(Base):
    __tablename__ = "group_assignments"

    id = Column(Integer, primary_key=True)
    member_client_id = Column(Integer, ForeignKey(Client.id))
    member_client = relationship("Client")
    member_group_id = Column(Integer, ForeignKey(ClientGroup.id))
    member_group = relationship("ClientGroup", foreign_keys=[member_group_id])
    client_group_id = Column(Integer, ForeignKey(ClientGroup.id))
    client_group = relationship("ClientGroup", foreign_keys=[client_group_id])

    def __init__(self, member_client_id, member_group_id, plugin_id):
        self.member_client_id = member_client_id
        self.member_group_id = member_group_id
        self.plugin_id = plugin_id

    def __repr__(self):
        return "<GroupAssignment id:{0}, member_client_id:{1}, member_group_id:{2}, client_group_id:{3}>".format(
                                    self.id, self.member_client_id, self.member_group_id, self.client_group_id)

Base.metadata.create_all(engine)
