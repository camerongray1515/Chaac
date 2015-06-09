var clients = {
    updateClientList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-clients").addClass("hidden");

        data.getClients(function(response) {
            var context = {
                "clients": response["clients"]
            };

            var source = $("#template-client").html();
            var template = Handlebars.compile(source);
            var html = template(context);

            $("#table-clients > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-clients").removeClass("hidden");
        });
    },
    addClient: function() {
        var formData = $(this).serializeArray();

        var formDict = {};
        for (var i = formData.length - 1; i >= 0; i--) {
            var entry = formData[i];
            formDict[entry["name"]] = entry["value"];
        };

        // Add the client and display the server's response.  If it was
        // successful then update the list of clients on the page
        data.addClient(formDict, function(response) {
            ui.showAlert("add-client-alert-container", "template-alert", response["success"], response["message"]);

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
