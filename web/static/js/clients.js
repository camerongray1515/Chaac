var clients = {
    updateClientList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-clients").addClass("hidden");

        data.getClients(function(response) {
            var context = {
                "clients": response["clients"]
            };

            $("#table-clients > tbody").html("");

            var html = ui.compileAndRenderTemplate("template-client", context);

            $("#table-clients > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-clients").removeClass("hidden");
        });
    },
    addClient: function() {
        var formDict = common.getFormDict(this);;

        // Add the client and display the server's response.  If it was
        // successful then update the list of clients on the page
        data.addClient(formDict, function(response) {
            ui.showAlert("add-client-alert-container", response["success"], response["message"]);

            if (response["success"]) {
                clients.updateClientList();
            }
        });

        return false; // Prevent the form from actually submitting
    }
}

$(document).ready(function() {
    clients.updateClientList(); // Load in list of clients on page load
    $("#form-add-client").submit(clients.addClient);
});
