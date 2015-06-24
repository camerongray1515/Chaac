import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from common.exceptions import GroupNotFoundException, InvalidUnitError

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

    def get_members(self, visited_group_ids=None, deduplicate=True):
        # Cannot pass an empty list as a default argument to a function in Python
        if visited_group_ids == None:
            visited_group_ids = []
        
        member_clients = []
        memberships = GroupAssignment.query.filter(GroupAssignment.client_group_id==self.id)
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
                    members = member.member_group.get_members(visited_group_ids, deduplicate=False)
                    member_clients += members # Appened the returned members onto the current list


        if deduplicate:
            # Now deduplicate the list of member clients
            member_clients_deduped = []
            visited_ids = []
            for client in member_clients:
                if client.id not in visited_ids:
                    member_clients_deduped.append(client)
                    visited_ids.append(client.id)
            return member_clients_deduped
        else:
            return member_clients

class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    version = Column(Float)

    def get_assigned_clients(self):
        assignments = PluginAssignment.query.filter(PluginAssignment.plugin_id==self.id)

        clients = []
        for assignment in assignments:
            if assignment.member_client:
                clients.append(assignment.member_client)
            else:
                clients += assignment.member_group.get_members()

        # Deduplicate the clients list
        clients_deduped = []
        visited_ids = []
        for client in clients:
            if client.id not in visited_ids:
                clients_deduped.append(client)
                visited_ids.append(client.id)
        return clients_deduped

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

    def __init__(self, plugin_id, member_client_id=None, member_group_id=None):
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

    def __init__(self, client_group_id, member_client_id=None, member_group_id=None):
        self.member_client_id = member_client_id
        self.member_group_id = member_group_id
        self.client_group_id = client_group_id

    def __repr__(self):
        return "<GroupAssignment id:{0}, member_client_id:{1}, member_group_id:{2}, client_group_id:{3}>".format(
                                    self.id, self.member_client_id, self.member_group_id, self.client_group_id)


class ScheduleInterval(Base):
    __tablename__ = "schedule_intervals"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship("Plugin")
    interval_seconds = Column(Integer)
    enabled = Column(Boolean)
    last_run = Column(DateTime)

    def __init__(self, plugin_id, interval_seconds):
        self.plugin_id = plugin_id
        self.interval_seconds = interval_seconds
        self.enabled = True

    def __repr__(self):
        return "<ScheduleInterval id:{0}, plugin_id:{1}, interval_seconds:{2}, enabled:{3}>".format(
            self.id, self.plugin_id, self.interval_seconds, self.enabled)

    # Logic to convert values with units into seconds and back
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
    SECONDS_IN_DAY = SECONDS_IN_HOUR * 24

    @hybrid_property
    def interval(self):
        seconds = self.interval_seconds
        # Start from hours and work downards to find the largest unit that the number of seconds divides
        # exactly into if we find one, return it.  If it doesn't divide exactly into anything, return 
        # the value in seconds
        if seconds % self.SECONDS_IN_DAY == 0:
            return (seconds / self.SECONDS_IN_DAY, "days")
        elif seconds % self.SECONDS_IN_HOUR == 0:
            return (seconds / self.SECONDS_IN_HOUR, "hours")
        elif seconds % self.SECONDS_IN_MINUTE == 0:
            return (seconds / self.SECONDS_IN_MINUTE, "minutes")
        else:
            return (seconds, "seconds")


    @interval.setter
    def interval(self, value_unit_tuple):
        (value, unit) = value_unit_tuple
        if unit == "seconds":
            seconds = value
        elif unit == "minutes":
            seconds = value * self.SECONDS_IN_MINUTE
        elif unit == "hours":
            seconds = value * self.SECONDS_IN_HOUR
        elif unit == "days":
            seconds = value * self.SECONDS_IN_DAY
        else:
            raise InvalidUnitError

        self.interval_seconds = seconds    


class ScheduleTimeSlot(Base):
    __tablename__ = "schedule_time_slots"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship("Plugin")
    time = Column(DateTime)
    enabled = Column(Boolean)

    def __init__(self, plugin_id, time):
        self.plugin_id = plugin_id
        self.time = time
        self.enabled = True

    def __repr__(self):
        return "<ScheduleTimeSlot id:{0}, plugin_id:{1}, time:{2}, enabled:{3}".format(self.id, self.plugin_id,
            self.time, self.days, self.enabled)


class ScheduleTimeSlotDay(Base):
    __tablename__ = "schedule_time_slot_days"

    id = Column(Integer, primary_key=True)
    time_slot_id = Column(Integer, ForeignKey(ScheduleTimeSlot.id))
    time_slot = relationship("ScheduleTimeSlot")
    day = Column(Integer)

    def __init__(self, time_slot_id, day):
        self.time_slot_id = time_slot_id
        self.day = day

    def __repr__(self):
        return "<ScheduleTimeSlotDay id:{0}, time_slot_id:{1}, day:{2}>".format(self.id, self.time_slot_id,
            self.day)

Base.metadata.create_all(engine)
