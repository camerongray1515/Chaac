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
    updateSlotList: function() {
        $("#slots-loading-message").removeClass("hidden");
        $("#table-slots").addClass("hidden");

        data.getSlots(function(response) {
            var templateContext = {"slots": []};
            var dayWords = [null, "Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun"];
            for (var i = response.slots.length - 1; i >= 0; i--) {
                var slot = response.slots[i];

                // Build up a string to represent the days
                dayString = "";
                for (var day = 1; day <= 7; day++) {
                    if (slot.days.indexOf(day) != -1) {
                        dayString += dayWords[day] + " ";
                    }
                }

                templateContext.slots.push({
                    "plugin": slot.plugin,
                    "hours": common.padNumber(slot.time.hours, 2),
                    "minutes": common.padNumber(slot.time.minutes, 2),
                    "days": dayString
                });
            }

            var html = ui.compileAndRenderTemplate("template-slots", templateContext);
            $("#table-slots > tbody").html(html);
        });

        $("#slots-loading-message").addClass("hidden");
        $("#table-slots").removeClass("hidden");
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
    },
    addSlot: function() {
        var formDict = common.getFormDict(this);

        data.addSlot(formDict, function(response) {
            ui.showAlert("add-new-alert-container", response["success"], response["message"]);
            schedule.updateSlotList();
        });

        return false;
    }
}

$(document).ready(function() {
    schedule.updatePluginList();
    schedule.updateIntervalList();
    schedule.updateSlotList();
    $("#form-add-interval").submit(schedule.addInterval);
    $("#form-add-slot").submit(schedule.addSlot);
});
