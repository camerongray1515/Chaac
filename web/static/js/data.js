var data = {
    getClients: function(callback) {
        $.get("/api/get_clients/", callback);
    }
}
