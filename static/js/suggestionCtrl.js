app.controller("suggestionCtrl", function($scope, $http, $sce, $window, loginService) {

    $scope.loginService = loginService;
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
    
    $scope.login = function(){
        loginService.login($scope.login_email, $scope.login_pw);
    }
    

    $scope.login = function(){
        loginService.login($scope.login_email, $scope.login_pw);
    }
    
    $scope.sendRegistration = function(){
        loginService.createAccount($scope.register_email,  $scope.register_pw, $scope.register_pw_confirm, $scope.register_username);
    }
    
    $scope.$watch('loginService.showRegister', function () {
        reloadPage();
    });
    
    $scope.$watch('loginService.showLogin', function () {
        reloadPage();
    });
    
    
    function clearFields(){
        $scope.login_email = "";
        $scope.login_pw = "";
        
        
        $scope.register_email = "";
        $scope.register_username = "";
        $scope.register_pw = "";
        $scope.register_pw_confirm = "";
    
        $scope.invalid_creds = false;
    }
    
    
    
});