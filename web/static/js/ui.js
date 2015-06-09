var ui = {
    alertTemplate: undefined,
    showAlert: function(alertContainerId, templateId, success, message) {
        var alertLevel = (success) ? "success" : "danger";
        var prefix = (success) ? "Success!" : "Error!";

        // Compile the template for the alert if it has not already been compiled
        if (ui.alertTemplate == undefined) {
            var source = $("#" + templateId).html();
            ui.alertTemplate = Handlebars.compile(source);
        }
        var html = ui.alertTemplate({"alert_level": alertLevel, "prefix": prefix, "message": message})

        $("#" + alertContainerId).hide();
        $("#" + alertContainerId).html(html);
        $("#" + alertContainerId).fadeIn();
    }
}
