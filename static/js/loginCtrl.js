app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.email = "";
    $scope.password = "";
    $scope.username="";
    $scope.createAccount = function(email, password, username){
        console.log("email: "+email);
        console.log("password: "+password);
        var data = {};
        data["email"] = email;
        data["password"] = password;
        data["username"] = username;
        $http.post('/api/login', data).then(function(response) {
            console.log("successful response");
            console.log("response token:" + response.data.token);
        });
    }
});
