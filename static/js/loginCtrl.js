app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.email = "";
    $scope.password = "";
    $scope.username="";
    $scope.logged_in = false;
    $scope.log_in_email = null;
    $scope.createAccount = function(email, password, username){
        console.log("email: "+email);
        console.log("password: "+password);
        var data = {};
        data["email"] = email;
        data["password"] = password;
        data["username"] = username;
        $http.post('/api/signup', data).then(function(response) {
            console.log("successful response");
            console.log("response token:" + response.data.token);
        });
    }
    
    $scope.logout = function(){
        var data = {};
        data["logout"] = true;
        $http.put("/api/login", data).then(function(response){
            if(response.data.success){
                console.log("logout success");    
            }else{
                console.log("logout fail");
            }
        });
    }
    
    
    $http.get("/api/login")
    .then(function(response) {
        if (response.data.user_email != null) {
            $scope.logged_in = true;
            $scope.log_in_email = response.data.user_email;
        }else{
            $scope.logged_in = false;
            $scope.log_in_email = null;
        }
    });
});
