from flask import Blueprint, jsonify, request
from common.models import session, Client, ClientGroup, GroupAssignment, Plugin

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
        print(member_groups)

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
            "version": plugin.version,
            "num_clients": len(plugin.get_assigned_clients())
        }
        plugins_list.append(plugin_dict)

    return jsonify(plugins=plugins_list)
