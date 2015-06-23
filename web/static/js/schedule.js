var schedule = {
    updatePluginList: function() {
        data.getPlugins(function(response) {
            var html = ui.compileAndRenderTemplate("template-plugin-option", response);
            $("select.plugin-list").html(html);
        });
    }
}

$(document).ready(function() {
    schedule.updatePluginList();
});
