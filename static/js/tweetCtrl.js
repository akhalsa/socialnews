app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.$watch('tweet_id', function () {
        if (typeof $scope.tweet_id != 'undefined' ) {
            console.log($scope.tweet_id);
            $http.get("/api/tweet/"+$scope.tweet_id)
            .then(function(response) {
              console.log("successfully called");  
            });
        }
        
        
    });
    
    $scope.sendComment = function(){
        console.log("sending");
    }
});
