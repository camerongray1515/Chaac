var ui = {
    alertTemplate: undefined,
    showAlert: function(alertContainerId, success, message) {
        // Hide any alerts that are currently being displayed to prevent confusion
        $(".alert").parent().hide()

        var alertLevel = (success) ? "success" : "danger";
        var prefix = (success) ? "Success!" : "Error!";

        // Compile the template for the alert if it has not already been compiled
        var html = ui.compileAndRenderTemplate("template-alert", {"alert_level": alertLevel, "prefix": prefix, "message": message});

        $("#" + alertContainerId).hide();
        $("#" + alertContainerId).html(html);
        $("#" + alertContainerId).fadeIn();
    },
    compiledTemplates: {},
    compileTemplate: function(templateId) {
        var source = $("#" + templateId).html();
        ui.compiledTemplates[templateId] = Handlebars.compile(source);
    },
    compileAndRenderTemplate: function(templateID, context) {
        // If the template has not yet been compiled, compile it, then render it and return the HTML
        if (ui.compiledTemplates[templateID] == undefined) {
            ui.compileTemplate(templateID);
        }
        var html = ui.compiledTemplates[templateID](context);

        return html;
    }
}
