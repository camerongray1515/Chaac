var groups = {
    updateGroupList: function() {
        $("#loading-message").removeClass("hidden");
        $("#table-groups").addClass("hidden");

        data.getGroups(function(response) {
            var context = {
                "groups": response["groups"]
            };

            $("#table-groups > tbody").html("");

            if (ui.compiledTemplates["template-group"] == undefined) {
                ui.compileTemplate("template-group");
            }
            var html = ui.compiledTemplates["template-group"](context);

            $("#table-groups > tbody").append(html);

            $("#loading-message").addClass("hidden");
            $("#table-groups").removeClass("hidden");
        });
    },
    addGroup: function() {
        var formData = $(this).serializeArray();

        var formDict = {};
        for (var i = formData.length - 1; i >= 0; i--) {
            var entry = formData[i];
            formDict[entry["name"]] = entry["value"];
        };

        // Add the group and display the server's response.  If it was
        // successful then update the list of groups on the page
        data.addGroup(formDict, function(response) {
            ui.showAlert("add-group-alert-container", "template-alert", response["success"], response["message"]);

            if (response["success"]) {
                groups.updateGroupList();
            }
        });

        return false; // Prevent the form from actually submitting
    }
}

$(document).ready(function() {
    groups.updateGroupList(); // Load in list of groups on page load
    $("#form-add-group").submit(groups.addGroup);
});
