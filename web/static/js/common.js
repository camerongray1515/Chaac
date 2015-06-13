var common = {
    getFormDict: function(formSelector) {
        var formData = $(formSelector).serializeArray();

        var formDict = {};
        for (var i = formData.length - 1; i >= 0; i--) {
            var entry = formData[i];
            formDict[entry["name"]] = entry["value"];
        };

        return formDict
    }
}
