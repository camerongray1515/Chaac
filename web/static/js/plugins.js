var plugins = {
    updatePluginList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-plugins").addClass("hidden");

        data.getPlugins(function(response) {
            $("#table-plugins > tbody").html("");

            var html = ui.compileAndRenderTemplate("template-plugin", response);

            $("#table-plugins > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-plugins").removeClass("hidden");
        });
    },
    assignPlugin: function() {
        var pluginID = $(this).attr("data-plugin-id");

        data.getPlugin(pluginID, function(response) {
            // If the plugin does not exist, handle the error and then abort rendering the modal
            if (!response.success) {
                ui.showAlert("installed-plugins-alert-container", false, response["message"]);
                return;
            }

            // Now render the template for the modal, put it on the page and then show it
            var html = ui.compileAndRenderTemplate("template-modal-assign-plugin", response);
            console.log(response);

            $("#compiled-modal").html(html);
            $("#compiled-modal > .modal").modal();
        });
    }
}

$(document).ready(function() {
    plugins.updatePluginList();
    $("#table-plugins").on("click", ".btn-assign-plugin", plugins.assignPlugin);
});
