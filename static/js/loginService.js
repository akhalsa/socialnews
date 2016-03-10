app.service('loginService', function(){
    this.logged_in = false;
    this.username = "";
    
    this.invalid_creds = false;
    this.showLogin = false;
    this.showRegister = false;
    
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
            console.log("successful response");
            this.logged_in = true;
            this.username = response.data.username;
            this.dismissPopups();
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 403) {
                console.log("got a 403");
            }
        });
        
    }
    
    this.login = function(email, pw){
        var data = {};
    
        data["email"] = email;
        data["password"] = pw;

        $http.post("/api/login", data).then(function successCallback(response){
            this.logged_in = response.data.logged_in;
            this.username = response.data.username;
            this.dismissPopups();
            
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 403) {
                console.log("got a 403");
                this.invalid_creds = true;
            }
        });
        

    }
    
    this.logout = function(){
        var data = {};
        console.log("logging out");
        data["logout"] = true;
        $http.put("/api/login", data).then(function(response){
            if (response.status == 200) {
                console.log("logout success");
                this.logged_in = false;
                this.username = "";
            }else{
                console.log("logout fail");
            }
        });
    }
    
    this.checkLoggedIn = function(){
        $http.get("/api/login")
        .then(function(response) {
            this.logged_in = response.data.logged_in;
            this.username =response.data.username;
        });
    }
    
    this.dismissPopups = function (){
        this.showLogin = false;
        this.showRegister = false;
        this.invalid_creds = false;
    }
    
    this.showLoginPopup = function(){
        this.showLogin = true;
        this.showRegister = false;
        this.invalid_creds = false;
    }
    
    this.showRegisterPopup = function(){
        this.showLogin = false;
        this.showRegister = true;
        this.invalid_creds = false;
    }
    
    
});
