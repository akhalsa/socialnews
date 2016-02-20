app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.text = "";
    $scope.handle = "";
    $scope.name = "";
    $scope.blurb = "";
    $scope.img_url = "";
    $scope.link_url = "";
    $scope.link_text = "";
    $scope.profile_image = "";
    
    $scope.new_comment_text = "";
    
    $scope.comments = [];
    
    
    $scope.$watch('tweet_id', function () {
        reloadPage();
    });
    
    $scope.redirectHome = function(){
        trackHomeLink();
        if( (typeof tracking == 'undefined')){
            document.location = "/";
        }else{
            document.location = "/?tracking=0"
        }
    }
    
    $scope.sendComment = function(){
        console.log("sending");
        
        var data = {};
        data["comment_text"] = $scope.new_comment_text;
        $http.post("/api/tweet/"+$scope.tweet_id, data).then(function(response){
            console.log("post successful");
            console.log(response.data.result);
            $scope.new_comment_text = "";
            reloadPage();
        });
        
    }
    
    $scope.sendCommentVote = function(comment_id, value){
        var data = {};
        data["comment_id"] = comment_id;
        data["vote_val"] = value;
        console.log( "sending payload: "+data);
        
        $http.post("/api/tweet/"+$scope.tweet_id+"/vote", data).then(function(response){
            console.log("post successful");
            console.log(response.data.success);
            console.log(response.data.msg);
            
        });
    }
    
    function reloadPage(){
        if (typeof $scope.tweet_id != 'undefined' ) {
            console.log($scope.tweet_id);
            $http.get("/api/tweet/"+$scope.tweet_id)
            .then(function(response) {
              console.log("successfully called");
              $scope.text = response.data.text;
              $scope.handle = response.data.twitter_handle;
              $scope.comments = response.data.comments;
              $scope.blurb = response.data.blurb;
              $scope.img_url = response.data.img_url;
              $scope.link_url = response.data.link_url;
              $scope.link_text = response.data.link_text;
              $scope.profile_image = response.data.profile_image;
              $scope.name = response.data.name;
            });
        }
        
    }
    
    
    
});
