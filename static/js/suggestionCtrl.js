app.controller("sharedLoginCtrl", function($scope, $http, $sce, $window, loginService) {

    
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
    $scope.throttled = false;
    
    
    $scope.comment_rate_limit = false;
    
    
    
    $scope.dismissPopups = function (){
        $scope.showLogin = false;
        $scope.showRegister = false;
        $scope.invalid_creds = false;
        $scope.throttled = false;
        
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
        $scope.throttled = false;
    }
    
    $scope.login = function(){
        var data = {};
    
        data["email"] = $scope.login_email;
        data["password"] = $scope.login_pw;

        $http.post("/api/login", data).then(function successCallback(response){
            //$scope.logged_in = response.data.logged_in;
            $scope.username = response.data.username;
            $scope.dismissPopups();
            //reloadPage();
            
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 403) {
                console.log("got a 403");
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
                //reloadPage();
            }else{
                console.log("logout fail");
            }
        });
    }

    
    
});