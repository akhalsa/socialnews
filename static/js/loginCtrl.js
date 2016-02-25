app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.email = "";
    $scope.password = "";
    $scope.username="";
    
    $scope.login_email = "";
    $scope.login_password = "";
    
    $scope.logged_in = false;
    $scope.logged_in_username = null;
    
    
    $scope.createAccount = function(email, password, username){
        console.log("email: "+email);
        console.log("password: "+password);
        var data = {};
        data["email"] = email;
        data["password"] = password;
        data["username"] = username;
        $http.post('/api/signup', data).then(function(response) {
            console.log("successful response");
            $scope.logged_in = true;
            $scope.logged_in_username = response.data.username;
        });
    }
    
    $scope.logout = function(){
        var data = {};
        console.log("logging out");
        data["logout"] = true;
        $http.put("/api/login", data).then(function(response){
            if(response.data.success){
                console.log("logout success");
                $scope.logged_in = false;
                $scope.logged_in_username = null;
            }else{
                console.log("logout fail");
            }
        });
    }
    
    $scope.login = function(){
        var data = {};
        data["email"] = $scope.login_email;
        data["password"] = $scope.login_password;
        $http.post("/api/login", data).then(function(response){
            $scope.logged_in = true;
            $scope.logged_in_username = response.data.username;
            console.log("username updated to: "+$scope.logged_in_username );
            
        });    
    }
    
    $http.get("/api/login")
    .then(function(response) {
        if (response.data.username != null) {
            $scope.logged_in = true;
            $scope.logged_in_username = response.data.username;
        }else{
            $scope.logged_in = false;
            $scope.logged_in_username = null;
        }
    });
});
