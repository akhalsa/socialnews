app.controller("newFiltraCtrl", function($scope, $http, $sce, $window) {
    $scope.logged_in = false;
    $scope.username = "";
    
    
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    $scope.current_path = [];
    $scope.time_frames = [{seconds:900, text:"Past 15 Minutes"}, {seconds:3600, text:"Past Hour"},
                           {seconds:10800, text:"Past 3 Hours"}, {seconds:43200, text:"Today"}];
    $scope.selected_time = 1;
    $scope.tweet_array = [];
    $scope.handle_list = [];
    $scope.peer_categories = [];
    
    $scope.showLogin = false;
    $scope.showRegister = false;
    
    $scope.login_email = "";
    $scope.login_pw = "";
    
    
    $scope.register_email = "";
    $scope.register_username = "";
    $scope.register_pw = "";
    $scope.register_pw_confirm = "";
    
    $scope.FEATURE_FLAG_NOMINATE = false;
    
    
    
    $scope.invalid_creds = false;
    
    
    $http.get("/api/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
        if (typeof $scope.category_name != 'undefined' ) {
            starting = checkForCatMatch( $scope.category_name);
            $scope.selected_top_index = starting[0];
            $scope.selected_secondary_index = starting[1];
            $scope.selected_third_index = starting[2];
        }
        reloadCurrentPath();
        checkLogin();
        loadTweets();
        loadHandles();
    });
    
    
    $scope.redirectHome = function(){
        if( (typeof tracking == 'undefined')){
            document.location = "/";
        }else{
            document.location = "/?tracking=0"
        }
    }
    
    $scope.selectionChange = function(top, second, third) {
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    $scope.refreshButton = function(){
        loadTweets();
        console.log("calling refresh");
    }
    
    $scope.vote = function(tweet_id, handle, value){
        data = {};
        data["tweet_id"] = tweet_id;
        skip = false;
        
        $scope.tweet_array.forEach(function(tweet) {
            if (tweet_id == tweet.id) {
                if (tweet.voted != 0) {
                    skip = true;
                }else{
                    tweet.voted = value;
                }
            }
        });
        
        if (skip) {
            console.log("skipping");
            return
        }
        $http.post( "/handle/"+handle+"/category/"+currentCatName()+"/upvote/"+value, data).then(function(response) {
            loadTweets();   
        });
    }
    
    
    //VIEW MODEL GENERATION ---- basically static methods for html
    
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
            if (response.status == 200) {
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
    
    $scope.breadCrumbSubSelect = function(bc_sub_index){
        if  ($scope.selected_secondary_index == -1) { 
            $scope.selected_secondary_index = bc_sub_index;
        } else if ($scope.selected_third_index == -1) {
            $scope.selected_third_index = bc_sub_index;
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    
    
    //PRIVATE METHODS
    function checkLogin(){
        $http.get("/api/login")
                .then(function(response) {
                    $scope.logged_in = response.data.logged_in;
                    $scope.username =response.data.username;
                });
    }
    
    function loadTweets(){
        var endPoint = "/reader/"+currentCatName()+"/time/"+$scope.time_frames[$scope.selected_time].seconds;
        $http.get(endPoint)
        .then(function(response) {
            
            $scope.tweet_array = response.data;
            $scope.tweet_array.forEach(function(tweet) {
                if (tweet.top_comment != null) {
                    console.log(tweet.text);
                    console.log("had comment");
                    console.log(tweet.top_comment.text);
                }
            });
        });
    }
    
    function loadHandles(){
        var endPoint = "/category/"+currentCatName();
        $http.get(endPoint)
        .then(function(response) {
            $scope.handle_list = response.data.handles;
            $scope.remaining_votes = response.data.remaining_votes;
        });
    }
    
    
    function checkForCatMatch(name) {
        for(i = 0; i<$scope.category_structure.length; i++){
            pos_name = getCatNameWithPositionVals(i, -1, -1);
            if (name.toUpperCase() === pos_name.toUpperCase() ) {
                return [i, -1, -1];
            }
            if (!$scope.category_structure[i].children) {
                continue;
            }
            
            for(j = 0; j<$scope.category_structure[i].children.length; j++){
                pos_name = getCatNameWithPositionVals(i, j, -1);
                if (name.toUpperCase() === pos_name.toUpperCase() ) {
                    return [i, j, -1];
                }
                if (!$scope.category_structure[i].children[j].children) {
                    continue;
                }
                for(k = 0; k < $scope.category_structure[i].children[j].children.length; k++){
                    pos_name = getCatNameWithPositionVals(i, j, k);
                    if (name.toUpperCase() === pos_name.toUpperCase() ) {
                        return [i, j, k];
                    }
                }
            }
        }
        return null;
    }
    
    function getCatNameWithPositionVals(i, j, k) {
        var cat_name = ""
        if ((j != -1) &&(k != -1)){
            cat_name = String($scope.category_structure[i].children[j].children[k].name);
        }else if (j != -1) {
            cat_name = String($scope.category_structure[i].children[j].name);
        }else {
            cat_name= String($scope.category_structure[i].name);
        }
        return cat_name;
    }
    
    function reloadCurrentPath(){
        if ($scope.selected_secondary_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name];
            $scope.peer_categories = $scope.category_structure[$scope.selected_top_index].children;
            
        } else if ($scope.selected_third_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name ];
            $scope.peer_categories = $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children;
        } else{
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children[$scope.selected_third_index].name ]
            $scope.peer_categories = [];
        }
    }
    
    function currentCatName() {
        return getCatNameWithPositionVals($scope.selected_top_index, $scope.selected_secondary_index, $scope.selected_third_index)
    }
    
    
    
});
