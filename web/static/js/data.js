var data = {
    getClients: function(callback) {
        $.get("/api/get_clients/", callback);
    },
    addClient: function(data, callback) {
        $.post("/api/add_client/", data, callback);
    }
}
