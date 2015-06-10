var groups = {
    updateGroupList: function() {
        // Not yet implemented
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
