
var app = angular.module("filtraApp", ['ui.bootstrap']);


app.filter('unsafeLink', function($sce) {
    return function(text) {
        var urlRegEx = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
        return $sce.trustAsHtml(text.replace(urlRegEx,"<a href='$1' target=\"_blank\" onclick=\"trackOutboundLink('$1');\">$1</a>"));
    };
});

app.filter('eliminateLink', function($sce) {
    return function(text) {
        var urlRegEx = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
        if (typeof(text) == "undefined")  {
            return $sce.trustAsHtml(text);
        }
        var res = text.match(urlRegEx);
        if (res == null) {
            return $sce.trustAsHtml("<span style=\"color:white;\">"+text+"</span>");
        }
        text = text.replace(urlRegEx,"");
        text = "<a href=\""+res[0]+"\" target=\"_blank\" onclick=\"trackOutboundLink(\""+res[0]+"\");>"+text+"</a>";
        return $sce.trustAsHtml(text);
        
    };
});


app.filter('matchTwitterName', function(){
    return function(handles, name){
        var out = [];
        for(i=0; i<handles.length; i++){
            if (handles[i].username == name) {
                out.push(handles[i]);
            }
        }
        return out;
    }
});

app.filter('skipLastBreadcrumb', function(){
    return function(current_path){
        var out = [];
        for(i=0; i<current_path.length; i++){
            if (i != current_path.length-1) {
                out.push(current_path[i]);
            }
        }
        return out;
    }
});

app.filter('dropProfileExtension', function(){
    return function(current_path){
        if (current_path) {
            var urlRegEx = /_normal/g;
            return current_path.replace(urlRegEx,"");
        }
        
    }
});

app.filter('convertSecondsToTimestamp', function(){
    return function(seconds){
        var t = new Date();
        t.setSeconds(t.getSeconds() - seconds);
        return t.toDateString() + " - "+t.toLocaleTimeString();
    }
})
