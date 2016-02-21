app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.text = "dummy";
    $scope.handle = "";
    $scope.name = "";
    $scope.blurb = "";
    $scope.img_url = "";
    $scope.link_url = "";
    $scope.link_text = "";
    $scope.profile_image = "";
    $scope.timestamp = "";
    
    
    $scope.new_comment_text = "";
    
    $scope.comments = [];
    
    $scope.logged_in = false;
    $scope.username = "";
    
    
    
    $scope.login_email = "";
    $scope.login_pw = "";
    
    
    $scope.register_email = "";
    $scope.register_username = "";
    $scope.register_pw = "";
    $scope.register_pw_confirm = "";
    
    
    
    $scope.invalid_creds = false;
    
    $scope.FindCredentialsFeatureFlag = false;
    
    $scope.showLogin = false;
    $scope.showRegister = false;
    
    
    
    
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
    
    $scope.convertSecondsToDeltaTime = function(seconds){
        if (seconds < 60) {
            return seconds+" sec";
        } else if (seconds < 3600) {
            var minutes = Math.round( seconds / 60);
            return minutes +" min";
        } else{
            var hours = Math.round( seconds / 3600);
            return hours + " hours";
        }
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
            reloadPage();
            
        });
    }
    
    $scope.dismissPopups = function (){
        $scope.showLogin = false;
        $scope.showRegister = false;
        $scope.invalid_creds = false;
        
        $scope.login_email = "";
        $scope.login_pw = "";
        
        
        $scope.register_email = "";
        $scope.register_username = "";
        $scope.register_pw = "";
        $scope.register_pw_confirm = "";
    }
    
    $scope.showLoginPopup = function(){
        $scope.showLogin = true;
        $scope.showRegister = false;
        $scope.invalid_creds = false;
    }
    
    $scope.showRegisterPopup = function(){
        $scope.showLogin = false;
        $scope.showRegister = true;
        $scope.invalid_creds = false;
    }
    
    $scope.login = function(){
        var data = {};
    
        data["email"] = $scope.login_email;
        data["password"] = $scope.login_pw;

        $http.post("/api/login", data).then(function successCallback(response){
            $scope.logged_in = response.data.logged_in;
            $scope.username = response.data.username;
            $scope.dismissPopups();
            reloadPage();
            
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 401) {
                console.log("got a 401");
                $scope.invalid_creds = true;
            }
        });
        

    }
    
    $scope.logout = function(){
        var data = {};
        console.log("logging out");
        data["logout"] = true;
        $http.put("/api/login", data).then(function(response){
            if(response.data.success){
                console.log("logout success");
                reloadPage();
            }else{
                console.log("logout fail");
            }
        });
    }
    
    
    $scope.createAccount = function(){
        
        
        
        console.log("email: "+$scope.register_email);
        console.log("username: "+$scope.register_username);
        console.log("pw: "+$scope.register_pw);
        console.log("pw confirm: "+$scope.register_pw_confirm);
        
        if ($scope.register_pw != $scope.register_pw_confirm) {
            alert("mismatched pw and pw confirm");
            return;
        }
        
        
        var data = {};
        data["email"] = $scope.register_email;
        data["password"] = $scope.register_pw;
        data["username"] = $scope.register_username;

        
        
        $http.post("/api/signup", data).then(function successCallback(response){
            console.log("successful response");
            $scope.logged_in = true;
            $scope.username = response.data.username;
            $scope.dismissPopups();
            reloadPage();
            
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 401) {
                console.log("got a 401");
            }
        });
        
    }
    
    
    // PRIVATE METHODS...not to be called from html
    
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
              $scope.timestamp = response.data.timestamp;
              console.log("got timestamp: "+$scope.timestamp);
            });
            
            $http.get("/api/login")
                .then(function(response) {
                    $scope.logged_in = response.data.logged_in;
                    $scope.username =response.data.username;
                });
        }
        
    }
    
    
    
});
