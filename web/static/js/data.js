var data = {
    getClients: function(callback) {
        $.get("/api/get_clients/", callback);
    },
    addClient: function(data, callback) {
        $.post("/api/add_client/", data, callback);
    },
    getGroups: function(callback) {
        $.get("/api/get_groups/", callback);
    },
    addGroup: function(data, callback) {
        $.post("/api/add_group/", data, callback);
    },
    getGroup: function(groupID, callback) {
        $.get("/api/get_group/", {"group_id": groupID}, callback);
    },
    editGroup: function(data, callback) {
        $.post("/api/edit_group/", data, callback);
    },
    getPlugins: function(callback) {
        $.get("/api/get_plugins/", callback);
    },
    getPlugin: function(pluginID, callback) {
        $.get("/api/get_plugin/", {"plugin_id": pluginID}, callback);
    },
    savePluginAssignments: function(data, callback) {
        $.post("/api/save_plugin_assignments/", data, callback);
    },
    addInterval: function(data, callback) {
        $.post("/api/add_interval/", data, callback);
    },
    getIntervals: function(callback) {
        $.get("/api/get_intervals/", callback);
    },
    addSlot: function(data, callback) {
        $.post("/api/add_slot/", data, callback);
    },
}
