function proxifyUrl(url) {
    console.log("proxyfing url: "+url);
    if (/^(f|ht)tps?:\/\//i.test(url)) {
        console.log("adding page load to: "+url);
        url = "/page_load/" + encodeURIComponent(url);
    }
    return url;
}

function unproxifyUrl(url) {
    console.log("unproxy method - "+url);
    if (/^page_load/i.test(url)) {
        console.log("running unproxy - "+url);
        return decodeURIComponent(url.split("/page_load/")[1]);
    }
    else
        return url;
    
}

var jqAjax = $.ajax;
$.ajax = function(settings) {
    if (settings && settings.url) {
        settings.url = proxifyUrl(settings.url);

        var settingsCopy = {
            url: unproxifyUrl(settings.url),
            complete: settings.complete,
            success: settings.success,
            error: settings.error
        };

        settings.complete = function(jqXHR, textStatus) {
            settingsCopy.complete(jqXHR, textStatus);
        };

        settings.success = function(data, textStatus, jqXHR) {
            settingsCopy.success(data, textStatus, jqXHR);
        };

        settings.error = function(jqXHR, textStatus, errorThrown) {
            settingsCopy.error(jqXHR, textStatus, errorThrown);
        };
    }
    jqAjax(settings);
};