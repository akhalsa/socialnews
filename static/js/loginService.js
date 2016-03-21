app.service('loginService', function($http){
    this.logged_in = false;
    this.username = "";
    
    this.invalid_creds = false;
    this.showLogin = false;
    this.showRegister = false;
    
    
    this.checkLoggedIn = function(){
        var login = this;
        $http.get("/api/login")
        .then(function(response) {
            login.logged_in = response.data.logged_in;
            login.username =response.data.username;
            console.log("username set: "+login.username);
        });
    }
    
    this.dismissPopups = function (){
        this.showLogin = false;
        this.showRegister = false;
        this.invalid_creds = false;
    }
    
    this.showLoginPopup = function(){
        console.log("show login popup");
        this.showLogin = true;
        this.showRegister = false;
        this.invalid_creds = false;
    }
    
    this.showRegisterPopup = function(){
        this.showLogin = false;
        this.showRegister = true;
        this.invalid_creds = false;
    }
    
    this.createAccount = function(email, password, pw_confirm, username){
        
        if (password != pw_confirm) {
            alert("mismatched pw and pw confirm");
            return;
        }

        
        var data = {};
        data["email"] = email;
        data["password"] = password;
        data["username"] = username;

        var login = this;
        
        $http.post("/api/signup", data).then(function successCallback(response){
            console.log("successful response");
            login.logged_in = true;
            login.username = response.data.username;
            login.dismissPopups();
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
        var login = this;
        $http.post("/api/login", data).then(function successCallback(response){
            login.logged_in = response.data.logged_in;
            login.username = response.data.username;
            login.dismissPopups();
            
        }, function errorCallback(response){
            console.log("got an error");
            if (response.status == 403) {
                console.log("got a 403");
                login.invalid_creds = true;
            }
        });
        

    }
    
    this.logout = function(){
        var data = {};
        console.log("logging out");
        data["logout"] = true;
        var login = this;
        $http.put("/api/login", data).then(function(response){
            if (response.status == 200) {
                console.log("logout success");
                login.logged_in = false;
                login.username = "";
                login.dismissPopups();
                login.checkLoggedIn();
                
            }else{
                console.log("logout fail");
            }
        });
    }
    
    
    
    
});
