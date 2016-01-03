var app = angular.module("filtraApp", []);

app.filter('unsafeLink', function($sce) {
    return function(text) {
        var urlRegEx = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
        return $sce.trustAsHtml(text.replace(urlRegEx,"<a href='$1' target=\"_blank\" onclick=\"trackOutboundLink('$1')\">$1</a>"));
    };
});

app.filter('matchTwitterName', function(){
    return function(handles, name){
        console.log("testing filter logging name: "+name+" and input array length: "+handles.length);
        var out = [];
        for(i=0; i<handles.length; i++){
            if (handles[i].name == name) {
                out.push(handles[i]);
            }
        }
        console.log("found out length: "+out.length);
        return out;
    }
});
