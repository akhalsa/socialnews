app.controller("suggestionCtrl", function($scope, $http, $sce, $window, loginService) {

    /*login variables */
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
    /* end of login variables */
    
    $scope.suggestion_text = "";
    
    $scope.suggestionlist = [];
    
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
        clearFields();
    });
    
    $scope.$watch('loginService.showLogin', function () {
        clearFields();
    });
    
    $scope.postSuggestion = function(){
        var data = {};
        data["text"] = $scope.suggestion_text;
        if ($scope.suggestion_text == "") {
            return;
        }
        $http.post("/api/suggestion", data).then(function successCallback(response){
            console.log("post successful");
            $scope.suggestion_text = "";
        }, function errorCallback(response){
            
        });
    }
    
    loadSuggestions();
    
    
    function loadSuggestions(){
        console.log("beginning to load suggestions");
        $http.get("/api/suggestion").then(function successCallback(response){
            console.log("get successful");
            $scope.suggestionlist = response.data.suggestions;
        }, function errorCallback(response){
            
        });
    }
    
    
    
    
    function clearFields(){
        console.log("clearing everything");
        $scope.login_email = "";
        $scope.login_pw = "";
        
        
        $scope.register_email = "";
        $scope.register_username = "";
        $scope.register_pw = "";
        $scope.register_pw_confirm = "";
    
        $scope.invalid_creds = false;
    }
    

    
    
});