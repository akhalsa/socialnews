app.controller("loginCtrl", function($scope, $http, $sce, $window) {
    $scope.username = "";
    $scope.password = "";
    $scope.createAccount = function(username, password){
        console.log("username: "+username);
        console.log("password: "+password);
        
    }
});
