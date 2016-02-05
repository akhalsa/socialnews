app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.text = "";
    $scope.handle = "";
    $scope.comments = [];
    
    
    $scope.$watch('tweet_id', function () {
        if (typeof $scope.tweet_id != 'undefined' ) {
            console.log($scope.tweet_id);
            $http.get("/api/tweet/"+$scope.tweet_id)
            .then(function(response) {
              console.log("successfully called");
              $scope.text = response.data.text;
              $scope.handle = response.data.twitter_handle;
              $scope.comments = response.data.comments;
              
            });
        }
        
        
    });
    
    $scope.sendComment = function(){
        console.log("sending");
        
        var data = {};
        data["comment_text"] = "Hi I'm a DIFFERENT comment!!!";
        $http.post("/api/tweet/"+$scope.tweet_id, data).then(function(response){
            console.log("post successful");
            console.log(response.data.result);
        });
        
    }
    
    $scope.sendCommentVote = function(comment_id, value){
        var data = {};
        data["comment_id"] = comment_id;
        data["vote_val"] = value;
        $http.post("/api/tweet/"+$scope.tweet_id+"/vote", data).then(function(response){
            console.log("post successful");
            console.log(response.data.result);
        });
        
    }
});
