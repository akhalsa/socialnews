app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.email = "";
    $scope.password = "";
    $scope.createAccount = function(email, password){
        console.log("email: "+email);
        console.log("password: "+password);
        var data = {};
        data["email"] = email;
        data["password"] = password;
        $http.post('/api/login', data).then(function(response) {
            console.log("successful response");
            console.log("response token:" + response.data.token);
        });
    }
});
