var plugins = {
    uploadPlugin: function(event) {
        event.preventDefault();
 
        var formData = new FormData($("#form-upload-plugin")[0]);

        data.uploadPlugin(formData, function(response) {
            ui.showAlert("install-plugin-alert-container", response["success"], response["message"]);
            plugins.updatePluginList();
        });
    },
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
    },
    saveAssignments: function() {
        var formDict = common.getFormDict(this);
        
        // Save the assignments and if we are successful, refresh the list and hide the modal.
        // Depending on whether we are succesful or not will decide where the alert is shown.
        data.savePluginAssignments(formDict, function(response) {
            if (response["success"]) {
                $("#compiled-modal > .modal").modal("hide");
                ui.showAlert("installed-plugins-alert-container", response["success"], response["message"]);
                plugins.updatePluginList();
            } else {
                ui.showAlert("assign-plugin-modal-alert-container", response["success"], response["message"]);
            }
        });

        return false; // Prevent the form from actually submitting
    }
}

$(document).ready(function() {
    plugins.updatePluginList();
    $("#table-plugins").on("click", ".btn-assign-plugin", plugins.assignPlugin);
    $("#compiled-modal").on("submit", "#form-assign-plugin", plugins.saveAssignments);
    $("#form-upload-plugin").submit(plugins.uploadPlugin);
});
