
var app = angular.module("filtraApp", ['ui.bootstrap']);


app.filter('unsafeLink', function($sce) {
    return function(text) {
        var urlRegEx = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
        return $sce.trustAsHtml(text.replace(urlRegEx,"<a href='$1' target=\"_blank\" onclick=\"trackOutboundLink('$1');\">$1</a>"));
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
        var urlRegEx = /_normal/g;
        return current_path.replace(urlRegEx,"");
    }
});

app.filter('nameToLink', function(){
    return function(name){
        
        return "/c/"+name;
    }
});
