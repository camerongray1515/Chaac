var clients = {
    updateClientList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-clients").addClass("hidden");

        data.getClients(function(response) {
            var context = {
                "clients": response["clients"]
            };

            var source = $("#template-client").html()
            var template = Handlebars.compile(source);
            var html = template(context);

            $("#table-clients > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-clients").removeClass("hidden");
        });
    }
}

$(document).ready(function() {
    clients.updateClientList(); // Load in list of clients on page load
});
