app.service('loginService', function(){
    this.logged_in = false;
    this.username = "";
    
    this.createAccount = function(email, password, pw_confirm, username){
        
        if (password != pw_confirm) {
            alert("mismatched pw and pw confirm");
            return;
        }

        
        var data = {};
        data["email"] = email;
        data["password"] = password;
        data["username"] = username;

        
        
        $http.post("/api/signup", data).then(function successCallback(response){

        }, function errorCallback(response){

        });
        
    }
    
    
});
