app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.username = "";
    $scope.password = "";
    $scope.createAccount = function(username, password){
        console.log("username: "+username);
        console.log("password: "+password);
        var data = {};
        data["username"] = username;
        data["password"] = password;
        $http.post('/api/login', data).then(function(response) {
            console.log("successful response");
        });
    }
});
