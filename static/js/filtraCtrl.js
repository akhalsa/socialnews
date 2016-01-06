app.controller("filtraCtrl", function($scope, $http, $sce) {
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    $scope.current_path = [];
    $scope.time_frames = [{seconds:900, text:"Past 15 Minutes"}, {seconds:3600, text:"Past Hour"},
                           {seconds:10800, text:"Past 3 Hours"}, {seconds:43200, text:"Today"}];
    $scope.selected_time = 0;
    $scope.tweet_array = [];
    $scope.handle_list = [];
    
    $scope.remaining_votes = 0;
    
    //popup vars
    $scope.nomination_visible = false;
    $scope.suggestion_list = [];
    $scope.handle_preview_html = "";
    $scope.handle_preview_html_safe = "";
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
        if (typeof $scope.category_name != 'undefined' ) {
            console.log("found: "+checkForCatMatch(0, -1, -1, $scope.category_name));
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles();
        
    });
    
    $scope.$watch('category_name', function () {
        console.log($scope.category_name);
        
    });
    
    
    // Configure user selections
    
    $scope.breadCrumbSelection = function(bc_index){
        if (bc_index == 0){
            $scope.selected_secondary_index = -1;
            $scope.selected_third_index = -1;
        }else if (bc_index == 1) {
            $scope.selected_third_index = -1;
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    $scope.selectionChange = function(top, second, third) {
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    
    $scope.timeChange = function(new_time_index){
        $scope.selected_time = new_time_index;
        loadTweets();
    }
    
    $scope.togglePopup = function(){
        console.log("toggle popup");
        $scope.nomination_visible = !$scope.nomination_visible;
    }
    
    $scope.voteForHandle = function(handle_string, value){
        handle = null;
        value = parseInt(value);
        for(i=0; i<$scope.handle_list.length; i++ ){
            if ($scope.handle_list[i].handle == handle_string) {
                handle = $scope.handle_list[i];
            }
        }
        if (handle == null) {
            console.log("handle match missing");
            return;
        }
        if ($scope.remaining_votes == 0) {
            return;
        }
        if (handle.vote_val != 0) {
            return;
        }
        handle.vote_val += value;
        
        if (value > 0) {
            handle.upvotes = parseInt(handle.upvotes) + value;
        }else if (value < 0) {
            handle.downvotes = parseInt(handle.downvotes) + value; 
        }
        $scope.remaining_votes -= 1;
        $http.post( "/handle/"+handle_string+"/category/"+currentCatName()+"/upvote/"+value).then(function(response) {});
    }
    
    $scope.runSearch = function(){
        if (($scope.search == "@") || ($scope.search == "")) {
            $scope.suggestion_list = [];
            return;
        }
        $scope.handle_preview_html = "";
        $scope.handle_preview_html_safe = "";
        $http.get("/twitter/search/"+$scope.search)
        .then(function(response) {
            if (response.data.search == $scope.search) {
                $scope.suggestion_list = response.data.handles;
                for (i=0; i<$scope.suggestion_list.length; i++) {
                    if (("@"+$scope.suggestion_list[i].screen_name) == $scope.search) {
                        loadTweetPreviews();
                    }
                }
            }
            
        });
    }
    
    $scope.updateSearch = function (new_val){
        $scope.search = new_val;
        loadTweetPreviews();
    }
    
    $scope.sendNomination = function(){
        var patt = /^@(\w){1,15}$/;
        if(patt.test($scope.search)){
            $scope.togglePopup();
            $http.post( "/handle/"+$scope.search+"/category/"+currentCatName()+"/upvote/"+1).then(function(response) {
                loadHandles();
            });
        }else{
            alert("Please enter a valid twitter handle");
        }
    }


    //VIEW MODEL GENERATION ---- basically static methods for html
    
    $scope.convertSecondsToDeltaTime = function(seconds){
        if (seconds < 60) {
            return seconds+" sec";
        } else if (seconds < 3600) {
            var minutes = Math.round( seconds / 60);
            return minutes +" min";
        } else{
            var hours = Math.round( seconds / 3600);
            return hours + " hours";
        }
    }
    
    
    // LOCAL PRIVATE STUFF... DO NOT CALL FROM HTML DIRECTLY

    function loadTweetPreviews() {
        $http.get("/twitter/timeline/"+$scope.search)
        .then(function(response) {
            $scope.handle_preview_html = "";
            for(i=0; i< response.data.length; i++){
                $scope.handle_preview_html += response.data[i];
            }
            $scope.handle_preview_html_safe = $sce.trustAsHtml($scope.handle_preview_html);
        });
    }
    function reloadCurrentPath(){
        if ($scope.selected_secondary_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name];
            
        } else if ($scope.selected_third_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name ]
        } else{
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children[$scope.selected_third_index].name ]
        }
    }
    
    function currentCatName() {
        return getCatNameWithPositionVals($scope.selected_top_index, $scope.selected_secondary_index, $scope.selected_third_index)
    }
    function getCatNameWithPositionVals(i, j, k) {
        var cat_name = ""
        if ((j != -1) &&(k != -1)){
            cat_name = String($scope.category_structure[i].children[j].children[k].name);
        }else if (j != -1) {
            cat_name = String($scope.category_structure[i].children[j].name);
        }else {
            cat_name= String($scope.category_structure[i].name);
        }
        return cat_name;
    }
    
    function loadTweets(){
        var endPoint = "/reader/"+currentCatName()+"/time/"+$scope.time_frames[$scope.selected_time].seconds;
        $http.get(endPoint)
        .then(function(response) {
            console.log("got a solid response");
            $scope.tweet_array = response.data;
        });
    }
    
    function loadHandles(){
        var endPoint = "/category/"+currentCatName();
        $http.get(endPoint)
        .then(function(response) {
            $scope.handle_list = response.data.handles;
            $scope.remaining_votes = response.data.remaining_votes;
        });
    }
    
    function checkForCatMatch(i, j, k, name) {
        //do check this round
        pos_name = getCatNameWithPositionVals(i, j, k);
        console.log("eval  i: "+i+" j: "+j+" k: "+k+" yields name: "+pos_name);
        if (name.toUpperCase() === pos_name.toUpperCase() ) {
            return (i, j, k)
        }
        //assume check failed.
        //whats the next position
        finished = true;
        if (i < ($scope.category_structure.length - 1) ){
            finished = false;
        } else if ($scope.category_structure[i].children && ( j < ($scope.category_structure[i].children.legnth -1) )) {
            finished = false;
        } else if ($scope.category_structure[i].children && $scope.category_structure[i].children[j] && (k < ($scope.category_structure[i].children[j].children.length -1))) {
            finished = false;
        }
        
        if (finished) {
            return null;
        }
        
        
        //ok not finished
        //now what?
        //is it time to increment i
        increment_i = true;
        if ($scope.category_structure[i].children && (j < ($scope.category_structure[i].children.length -1))) {
            increment_i = false;
        }else if ($scope.category_structure[i].children && $scope.category_structure[i].children[j].children &&  (k < ($scope.category_structure[i].children[j].children.length -1))  ) {
            increment_i = false;
        }
        
        if (increment_i) {
            return checkForCatMatch(i+1, -1, -1, name);
        }
        
        
        
        //ok not finished and not time to increment i, is it time to increment j
        increment_j = true;
        if ($scope.category_structure[i].children && $scope.category_structure[i].children[j].children &&  (k < ($scope.category_structure[i].children[j].children.length -1))  ) {
            increment_j = false;
        }
        
        if (increment_j) {
            return checkForCatMatch(i, j+1, -1, name);
        }
        
        //not finished, not increment i, not increment j -> increment k!
        
        return checkForCatMatch(i, j, k+1, name);
        
    }
    

    
});
