import datetime
import configparser
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from common.exceptions import GroupNotFoundException, InvalidUnitError

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

engine = create_engine(config["Database"]["connection_string"])
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
    filename = Column(Text)
    class_name = Column(Text)

    results = relationship("PluginResult",
            cascade="all, delete, delete-orphan", backref="plugin")

    assignments = relationship("PluginAssignment",
            cascade="all, delete, delete-orphan", backref="plugin")

    intervals = relationship("ScheduleInterval",
            cascade="all, delete, delete-orphan", backref="plugin")

    slots = relationship("ScheduleTimeSlot",
            cascade="all, delete, delete-orphan", backref="plugin")

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

    def __init__(self, name, description, version, filename, class_name):
        self.name = name
        self.description = description
        self.version = version
        self.filename = filename
        self.class_name = class_name

    def __repr__(self):
        return "<Plugin id:{0}, name:{1}, version:{2}>".format(self.id,
                self.name, self.version)


class PluginResult(Base):
    __tablename__ = "plugin_results"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
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
    interval_seconds = Column(Integer)
    enabled = Column(Boolean)
    last_run = Column(DateTime)

    def __init__(self, plugin_id, interval_value, interval_unit="seconds"):
        self.plugin_id = plugin_id
        self.interval = (interval_value, interval_unit)
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
        value = int(value)
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
    time = Column(Time)
    enabled = Column(Boolean)

    @hybrid_property
    def days(self):
        days = ScheduleTimeSlotDay.query.filter(ScheduleTimeSlotDay.time_slot==self)

        day_list = []
        for day in days:
            day_list.append(day.day)

        return day_list

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
