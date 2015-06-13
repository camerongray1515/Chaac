var plugins = {
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
    }
}

$(document).ready(function() {
    plugins.updatePluginList();
});
