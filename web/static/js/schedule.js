var schedule = {
    updateIntervalList: function() {
        // NOT YET IMPLEMENTED
    },
    updatePluginList: function() {
        data.getPlugins(function(response) {
            var html = ui.compileAndRenderTemplate("template-plugin-option", response);
            $("select.plugin-list").html(html);
        });
    },
    addInterval: function() {
        var formDict = common.getFormDict(this);

        data.addInterval(formDict, function(response) {
            ui.showAlert("add-new-alert-container", response["success"], response["message"]);
            schedule.updateIntervalList();
        });

        return false;
    }
}

$(document).ready(function() {
    schedule.updatePluginList();
    $("#form-add-interval").submit(schedule.addInterval);
});
