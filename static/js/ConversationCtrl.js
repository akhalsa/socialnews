app.controller("ConversationCtrl", function($scope, $http, $sce, $window) {
    
    
    $http.get("/api/conversations")
    .then(function(response) {
        convos = response.data;
        for(i=0; i<convos.length; i++ ){
            conversation = convos[i];
            console.log("in cat: "+conversation.category_name+" we had a conversation around: "+conversation.representative_tweet);
        }
    });
        
});