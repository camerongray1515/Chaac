from flask import Blueprint, jsonify, request, current_app
from common.models import session, Client, ClientGroup, GroupAssignment, Plugin, PluginAssignment, ScheduleInterval, ScheduleTimeSlot, ScheduleTimeSlotDay
from common.exceptions import InvalidUnitError
import datetime
import itertools
import tarfile
import json
import os

api = Blueprint('api', __name__, url_prefix='/api')

@api.route("/get_clients/")
def get_clients():
    clients = Client.query.all()

    client_list = []

    for client in clients:
        client_dict = {
            "id": client.id,
            "name": client.name,
            "description": client.description,
            "ip_address": client.ip_address,
            "port": client.port
        }
        client_list.append(client_dict)

    return jsonify(clients=client_list)

@api.route("/add_client/", methods=["POST"])
def add_client():
    c = Client( name=request.form.get("client-name").strip(),
                description=request.form.get("client-description").strip(),
                ip_address=request.form.get("client-ip").strip(),
                port=request.form.get("client-port").strip())

    response = {"success": True, "message": "Client was added successfully"}
    # Now validate the client before adding it to the database

    # Check required fields are filled in
    if not (c.name and c.ip_address and c.port):
        response = {"success": False, "message": "Name, IP Address and Port are required"}
    elif not c.port.isnumeric(): # Check that the port is numeric
        response = {"success": False, "message": "Port must be a number"}

    # Finally add the client to the database if all checks passed
    if response["success"]:
        session.add(c)
        session.commit()

    return jsonify(response)

@api.route("/get_groups/")
def get_groups():
    groups = ClientGroup.query.all()

    group_list = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "num_clients": len(group.get_members())
        }
        group_list.append(group_dict)

    return jsonify(groups=group_list)

@api.route("/add_group/", methods=["POST"])
def add_group():
    g = ClientGroup( name=request.form.get("group-name").strip(),
                     description=request.form.get("group-description").strip())

    response = {"success": True, "message": "Group was added successfully"}
    # Now validate the group before adding it to the database

    # Check that name is filled in
    if not (g.name):
        response = {"success": False, "message": "Name is required"}

    # Finally add the client to the database if all checks passed
    if response["success"]:
        session.add(g)
        session.commit()

    return jsonify(response)

@api.route("/get_group/")
def get_group():
    group_id = request.args.get("group_id")

    # Fetch the group itself from the database (name, description)
    group = ClientGroup.query.get(group_id)

    if not group:
        return jsonify({"success": False, "message": "Group not found"})

    # Get all groups and all clients in the system
    groups = ClientGroup.query.filter(ClientGroup.id != group_id)
    clients = Client.query.all()

    # Convert these into a dictionary where the value is the group id and which
    # indexes another dicitonary containing the client/group name and a boolean
    # defining whether it is a member of this group or not
    group_members = {}
    client_members = {}
    # Say that none of them are in the group at first, we will then mark the ones
    # that are in the group later on
    for g in groups:
        entry = {
            "id": g.id,
            "name": g.name,
            "is_member": False
        }
        group_members[g.id] = entry

    for c in clients:
        entry = {
            "id": c.id,
            "name": c.name,
            "is_member": False
        }
        client_members[c.id] = entry

    # Now get all members of the group and go through them, for each of them, mark
    # them as being a member in the above two dictionaries
    group_memberships = GroupAssignment.query.filter(GroupAssignment.client_group_id==group_id)
    for group_membership in group_memberships:
        # Check if this is a group or a client and update the appropriate dictionary
        if group_membership.member_group:
            group_members[group_membership.member_group.id]["is_member"] = True
        else:
            client_members[group_membership.member_client.id]["is_member"] = True


    response = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "members": {
            "groups": group_members,
            "clients": client_members
        },
        "success": True
    }

    return jsonify(response)

@api.route("/edit_group/", methods=["POST"])
def edit_group():
    group_id = request.form.get("group-id")

    # Get the group and if it doesn't exist, throw an error
    group = ClientGroup.query.get(group_id)

    if not group:
        return jsonify({"success": False, "message": "Group not found"})

    response = {"success": True, "message": "Group has been edited successfully"}

    # Update the name and description of the group
    name = request.form.get("group-name")
    description = request.form.get("group-description")

    # Name is required
    if not name.strip():
        response = {"success": False, "message": "Name is required"}

    if response["success"]:
        group.name = name
        group.description = description

        # Now remove all group/client assignments from this group and insert all
        # the ones that were specified in the request
        GroupAssignment.query.filter(GroupAssignment.client_group_id==group_id).delete()

        member_groups = request.form.getlist("member-group[]")
        member_clients = request.form.getlist("member-client[]")

        if member_groups:
            for member_id in member_groups:
                assignment = GroupAssignment(client_group_id=group_id, member_group_id=member_id)
                session.add(assignment)

        if member_clients:
            for member_id in member_clients:
                assignment = GroupAssignment(client_group_id=group_id, member_client_id=member_id)
                session.add(assignment)

        # Commit all changes to the database
        session.commit()

    return jsonify(response)

@api.route("/get_plugins/")
def get_plugins():
    plugins = Plugin.query.all()

    plugins_list = []
    for plugin in plugins:
        plugin_dict = {
            "id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "num_clients": len(plugin.get_assigned_clients())
        }
        plugins_list.append(plugin_dict)

    return jsonify(plugins=plugins_list)

@api.route("/get_plugin/")
def get_plugin():
    plugin_id = request.args.get("plugin_id")

    # Fetch the plugin itself from the database (name, description)
    plugin = Plugin.query.get(plugin_id)

    if not plugin:
        return jsonify({"success": False, "message": "Plugin not found"})

    # Get all groups and all clients in the system
    groups = ClientGroup.query.all()
    clients = Client.query.all()

    # Convert these into a dictionary where the value is the group id and which
    # indexes another dicitonary containing the client/group name and a boolean
    # defining whether this plugin is assigned to it or not
    assigned_groups = {}
    assigned_clients = {}
    # Say that no clients/groups are assigned at first, we will then mark the ones
    # that are assigned later on
    for g in groups:
        entry = {
            "id": g.id,
            "name": g.name,
            "is_assigned": False
        }
        assigned_groups[g.id] = entry

    for c in clients:
        entry = {
            "id": c.id,
            "name": c.name,
            "is_assigned": False
        }
        assigned_clients[c.id] = entry

    # Now get all assignments to the plugin and go through them, for each of them, mark
    # them as being assigned in above two dictionaries
    plugin_assignments = PluginAssignment.query.filter(PluginAssignment.plugin_id==plugin_id)
    for assignment in plugin_assignments:
        # Check if this is a group or a client and update the appropriate dictionary
        if assignment.member_group:
            assigned_groups[assignment.member_group.id]["is_assigned"] = True
        else:
            assigned_clients[assignment.member_client.id]["is_assigned"] = True


    response = {
        "id": plugin.id,
        "name": plugin.name,
        "description": plugin.description,
        "assignments": {
            "groups": assigned_groups,
            "clients": assigned_clients
        },
        "success": True
    }

    return jsonify(response)

@api.route("/save_plugin_assignments/", methods=["POST"])
def save_plugin_assignments():
    plugin_id = request.form.get("plugin-id")

    # Get the plugin and if it doesn't exist, throw an error
    plugin = Plugin.query.get(plugin_id)

    if not plugin:
        return jsonify({"success": False, "message": "Plugin not found"})

    response = {"success": True, "message": "Plugin assignments have been updated successfully"}

    # Now remove all assignments for this plugin and then add the ones specified in the request
    PluginAssignment.query.filter(PluginAssignment.plugin_id==plugin_id).delete()

    assigned_groups = request.form.getlist("assigned-group[]")
    assigned_clients = request.form.getlist("assigned-client[]")

    if assigned_groups:
        for member_id in assigned_groups:
            assignment = PluginAssignment(plugin_id=plugin_id, member_group_id=member_id)
            session.add(assignment)

    if assigned_clients:
        for member_id in assigned_clients:
            assignment = PluginAssignment(plugin_id=plugin_id, member_client_id=member_id)
            session.add(assignment)

    # Commit all changes to the database
    session.commit()

    return jsonify(response)

@api.route("/add_interval/", methods=["POST"])
def add_interval():
    plugin_id = request.form.get("plugin-id")
    interval_unit = request.form.get("interval-unit")

    try:
        interval_value = int(request.form.get("interval-value"))
    except ValueError:
        return jsonify({"success": False, "message": "Interval value must be a number"})

    # All fields above are required and the interval value must be greater than 0
    if not (plugin_id and interval_value and interval_value):
        return jsonify({"success": False, "message": "All fields are required"})
    elif interval_value < 1:
        return jsonify({"success": False, "message": "Interval value must be at least 1"})

    if not Plugin.query.get(plugin_id):
        return jsonify({"success": False, "message": "Specified plugin does not exist"})

    try:
        i = ScheduleInterval(plugin_id=plugin_id, interval_value=interval_value, interval_unit=interval_unit)
    except InvalidUnitError:
        return jsonify({"success": False, "message": "Invalid unit specified"})

    session.add(i)
    session.commit()

    return jsonify({"success": True, "message": "Interval has been added successfully"})

@api.route("/get_intervals/")
def get_intervals():
    intervals = ScheduleInterval.query.all()

    intervals_list = []
    for interval in intervals:
        interval_dict = {
            "plugin": {
                "id": interval.plugin.id,
                "name": interval.plugin.name
            },
            "time": interval.interval[0],
            "unit": interval.interval[1],
            "seconds": interval.interval_seconds,
            "enabled": interval.enabled,
            "last_run": interval.last_run
        }

        intervals_list.append(interval_dict)

    return jsonify({"success": True, "intervals": intervals_list})

@api.route("/add_slot/", methods=["POST"])
def add_slot():
    plugin_id = request.form.get("plugin-id")

    try:
        slot_hour = int(request.form.get("slot-hour"))
        slot_minute = int(request.form.get("slot-minute"))
        weekdays = map(int, request.form.getlist("weekdays[]"))
    except ValueError:
        return jsonify({"success": False, "message": "Hour and minute of the time slot must be numbers"})

    # Generate multiple iterators since we need to go through the weekdays list twice
    (weekdays_it1, weekdays_it2) = itertools.tee(weekdays, 2)

    if not Plugin.query.get(plugin_id):
        return jsonify({"success": False, "message": "Specified plugin does not exist"})

    if slot_hour < 0 or slot_hour > 23:
        return jsonify({"success": False, "message": "Hour must be between 0 and 23"})

    if slot_minute < 0 or slot_minute > 59:
        return jsonify({"success": False, "message": "Minute must be between 0 and 59"})

    for weekday in weekdays_it1:
        if weekday < 1 or weekday > 7:
            return jsonify({"success": False, "message": "One or more of the specified weekdays was invalid"})

    # Input validation complete, start inserting data
    time = datetime.time(slot_hour, slot_minute)

    slot = ScheduleTimeSlot(plugin_id=plugin_id, time=time)
    session.add(slot)
    session.commit() # Commit so that the slot gets its ID assigned for use with adding the weekdays

    for weekday in weekdays_it2:
        day = ScheduleTimeSlotDay(time_slot_id=slot.id, day=weekday)
        session.add(day)

    session.commit()

    return jsonify({"success": True, "message": "Time slot has been added successfully"})

@api.route("/get_slots/")
def get_slots():
    slots = ScheduleTimeSlot.query.all()

    slots_list = []
    for slot in slots:
        slot_dict = {
            "plugin": {
                "id": slot.plugin.id,
                "name": slot.plugin.name
            },
            "time": {
                "hours": slot.time.hour,
                "minutes": slot.time.minute
            },
            "days": slot.days,
            "enabled": slot.enabled
        }

        slots_list.append(slot_dict)

    return jsonify({"success": True, "slots": slots_list})

@api.route("/upload_plugin/", methods=["POST"])
def upload_plugin():
    # Try to open the plugin file (which is just a .tar.gz archive) and
    # read the info.json file contained within which contains all the
    # information about the plugin that we need in order to install it
    try:
        plugin_tar = tarfile.open(fileobj=request.files["plugin-file"],
                mode="r:gz")
    except ValueError:
        return jsonify({"success": False, "message": "No plugin selected"})
    except tarfile.ReadError:
        return jsonify({"success": False, "message": "Could not read plugin "
                "file, is it a valid .tar.gz archive?"})

    try:
        info_file = plugin_tar.extractfile("./info.json")
    except KeyError:
        return jsonify({"success": False, "message": "Plugin does not contain "
                "an info.json file"})

    try:
        plugin_info = json.loads(info_file.read().decode("UTF-8"))
    except ValueError:
        return jsonify({"success": False, "message": "The plugin's info.json "
                "file could not be understood"})

    # Check if the plugin is already installed, if it is update it.
    # If we have never seen this plugin before, install it.
    installed_plugins = Plugin.query.filter(
            Plugin.name==plugin_info["plugin_name"]).all()
    plugin_filename = plugin_info["plugin_name"] + ".tar.gz"
    if installed_plugins:
        plugin = installed_plugins[0]

        plugin.name = plugin_info["plugin_name"]
        plugin.description = plugin_info["description"]
        plugin.version = plugin_info["version"]
        plugin.filename = plugin_filename
        plugin.class_name = plugin_info["class_name"]
        action_taken = "updated"
    else:
        plugin = Plugin(name=plugin_info["plugin_name"],
                description=plugin_info["description"],
                version=plugin_info["version"],
                filename=plugin_filename,
                class_name=plugin_info["class_name"])
        session.add(plugin)
        action_taken = "installed"
    session.commit()

    # Finally save the file out to disk
    request.files["plugin-file"].seek(0)
    request.files["plugin-file"].save(os.path.join(
            current_app.config["PLUGIN_REPOSITORY"], plugin_filename))

    return jsonify({"success": True, "message":
            "Plugin has been {0} successfully".format(action_taken)})
