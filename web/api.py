from flask import Blueprint, jsonify, request
from common.models import session, Client, ClientGroup

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
            "num_clients": len(ClientGroup.get_members(group))
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
