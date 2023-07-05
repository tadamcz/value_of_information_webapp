/* Project specific Javascript goes here. */
function formatDate(date) {
    let dayOfMonth = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();
    let hour = date.getHours();
    let minutes = date.getMinutes();
    let diffMs = new Date() - date;
    let diffSec = diffMs / 1000;
    let diffMin = diffSec / 60;
    let diffHour = diffMin / 60;

    // formatting
    year = year.toString().slice(-2);
    month = month < 10 ? '0' + month : month;
    dayOfMonth = dayOfMonth < 10 ? '0' + dayOfMonth : dayOfMonth;
    hour = hour < 10 ? '0' + hour : hour;
    minutes = minutes < 10 ? '0' + minutes : minutes;

    if (diffSec < 1) {
        return 'right now';
    } else if (diffMin < 1) {
        return `${diffSec.toFixed(0)} sec. ago`
    } else if (diffHour < 1) {
        return `${diffMin.toPrecision(2)} min. ago`
    } else {
        return `${dayOfMonth}.${month}.${year} ${hour}:${minutes}`
    }
}


const prior_family_selector = $('select[name=prior_family]');

prior_family_selector.change(function () {
    const family = this.value;

    const normal_rows = $("[name=normal_prior_sd], [name=normal_prior_ev]").closest(".row");
    const lognormal_rows = $("[name=lognormal_prior_sd], [name=lognormal_prior_ev]").closest(".row");
    const metalog_rows = $(".row.family-metalog");

    normal_rows.hide()
    lognormal_rows.hide()
    metalog_rows.hide()

    if (family === "lognormal") {
        lognormal_rows.show()
    }
    if (family === "normal") {
        normal_rows.show()
    }
    if (family === "metalog") {
        metalog_rows.show()
    }

});

prior_family_selector.trigger("change")


// listen for the message 'metalog_params' from the iframe
window.addEventListener('message', function (event) {
    if (event.data.type === 'metalog_params') {
        console.log("received", event.data.data);
        const data = JSON.stringify(event.data.data);
        // Place the JSON in the hidden input field with name 'metalog_prior_data'
        $("[name=metalog_prior_data]").val(data);
    }
});

// On load
const iframeContainer = $("#iframecontainer")
var fieldData = $("[name=metalog_prior_data]").val()
fieldData = JSON.parse(fieldData);
if (fieldData) {
    formData = fieldData.form;
    queryString = $.param(formData);
}
else {
    queryString = "";
}
src = "https://mdist." + window.location.hostname + "?" + queryString;
iframeContainer.html(
    `<iframe id="metalogframe" class="border" src="${src}" width="1100" height="1050"></iframe>`
)