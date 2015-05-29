import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from exceptions import GroupNotFoundException

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

    @staticmethod
    def get_members(client_group, visited_group_ids=[]):
        if (client_group == None):
            raise GroupNotFoundException

        member_clients = []
        memberships = GroupAssignment.query.filter(GroupAssignment.client_group_id==client_group.id)
        for member in memberships:
            # If the member is a client, add it to the list, if it is a group, recurse
            if member.member_client:
                member_clients.append(member.member_client)
            else:
                # If we have not already retrieved members from this group, get them.
                # otherwise do not, this will prevent us getting stuck in loops of
                # visiting the same groups 
                if member.member_group_id not in visited_group_ids:
                    visited_group_ids.append(member.member_group_id)
                    members = ClientGroup.get_members(member.member_group, visited_group_ids)
                    member_clients += members # Appened the returned members onto the current list

        # Now deduplicate the list of member clients
        member_clients_deduped = []
        visited_ids = []
        for client in member_clients:
            if client.id not in visited_ids:
                member_clients_deduped.append(client)
                visited_ids.append(client.id)
        return member_clients_deduped


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

if __name__ == "__main__":
    group = ClientGroup.query.get(5)
    print(ClientGroup.get_members(group))
