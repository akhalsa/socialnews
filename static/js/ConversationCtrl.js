app.controller("ConversationCtrl", function($scope, $http, $sce, $window) {
    
    $scope.conversations = []
    
    
    $http.get("/api/conversations")
    .then(function(response) {
        $scope.conversations = response.data;
        for(i=0; i<$scope.conversations.length; i++ ){
            conversation = $scope.conversations[i];
            console.log("in cat: "+conversation.category_name+" we had a conversation around: "+conversation.representative_tweet);
        }
    });
        
});