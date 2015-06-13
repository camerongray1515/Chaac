var common = {
    getFormDict: function(formSelector) {
        var formData = $(formSelector).serializeArray();

        var formDict = {};
        for (var i = formData.length - 1; i >= 0; i--) {
            var entry = formData[i];

            // Check if this is to be dealt with as an array (name ends in []) or not
            // and treat it appropriately
            if (entry["name"].slice(-2) == "[]") {
                // Create an array if it does not already exist and then push the value
                // onto it
                if (formDict[entry["name"]] == undefined) {
                    formDict[entry["name"]] = [];
                }
                formDict[entry["name"]].push(entry["value"])
            } else {
                formDict[entry["name"]] = entry["value"];
            }
        };

        return formDict
    }
}
