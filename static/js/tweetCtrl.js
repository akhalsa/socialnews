app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.$watch('tweet_id', function () {
        if (typeof $scope.tweet_id != 'undefined' ) {
            console.log($scope.tweet_id);
            $http.get("/api/tweet/"+$scope.tweet_id)
            .then(function(response) {
              console.log("successfully called");
              console.log(response.data.text);
            });
        }
        
        
    });
    
    $scope.sendComment = function(){
        console.log("sending");
        
        var data = {};
        data["comment_text"] = "Hi I'm a comment!!!";
        $http.post("/api/tweet/"+$scope.tweet_id, data).then(function(response){
            console.log("post successful");
            console.log(response.data.result);
        });
        
    }
});
