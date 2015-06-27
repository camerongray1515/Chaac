var schedule = {
    updateIntervalList: function() {
        $("#intervals-loading-message").removeClass("hidden");
        $("#table-intervals").addClass("hidden");

        data.getIntervals(function(response) {
            var html = ui.compileAndRenderTemplate("template-intervals", response);
            $("#table-intervals > tbody").html(html);

            $("#intervals-loading-message").addClass("hidden");
            $("#table-intervals").removeClass("hidden");
        });
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
    schedule.updateIntervalList();
    $("#form-add-interval").submit(schedule.addInterval);
});
