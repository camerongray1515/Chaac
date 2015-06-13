var groups = {
    updateGroupList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-groups").addClass("hidden");

        data.getGroups(function(response) {
            var context = {
                "groups": response["groups"]
            };

            $("#table-groups > tbody").html("");

            var html = ui.compileAndRenderTemplate("template-group", context);

            $("#table-groups > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-groups").removeClass("hidden");
        });
    },
    addGroup: function() {
        var formDict = common.getFormDict(this);

        // Add the group and display the server's response.  If it was
        // successful then update the list of groups on the page
        data.addGroup(formDict, function(response) {
            ui.showAlert("add-group-alert-container", response["success"], response["message"]);

            if (response["success"]) {
                groups.updateGroupList();
            }
        });

        return false; // Prevent the form from actually submitting
    },
    editGroup: function() {
        var groupID = $(this).attr("data-group-id");

        data.getGroup(groupID, function(response) {
            // If the group does not exist, handle the error and then abort rendering the modal
            if (!response.success) {
                ui.showAlert("existing-groups-alert-container", false, response["message"]);
                return;
            }

            // Now render the template for the modal, put it on the page and then show it
            var html = ui.compileAndRenderTemplate("template-modal-edit-group", response);

            $("#compiled-modal").html(html);
            $("#compiled-modal > .modal").modal();
        });
    },
    saveGroup: function() {
        var formDict = common.getFormDict(this);
        
        // Save the group and if we are successful, refresh the list and hide the modal.
        // Depending on whether we are succesful or not will decide where the alert is shown.
        data.editGroup(formDict, function(response) {
            if (response["success"]) {
                $("#compiled-modal > .modal").modal("hide");
                ui.showAlert("existing-groups-alert-container", response["success"], response["message"]);
                groups.updateGroupList();
            } else {
                ui.showAlert("edit-group-modal-alert-container", response["success"], response["message"]);
            }
        });

        return false; // Prevent the form from actually submitting
    }
}

$(document).ready(function() {
    groups.updateGroupList(); // Load in list of groups on page load
    $("#form-add-group").submit(groups.addGroup);
    $("#table-groups").on("click", ".btn-edit-group", groups.editGroup);
    $("#compiled-modal").on("submit", "#form-edit-group", groups.saveGroup);
});
