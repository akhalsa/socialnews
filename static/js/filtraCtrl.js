app.controller("filtraCtrl", function($scope, $http) {
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
    $scope.suggestion_list = [];
    $scope.remaining_votes = 0;
    $scope.nomination_visible = false;
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles()
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
        console.log("changing to: "+top);
        console.log("changing to second: "+second);
        console.log("changing to third: "+third);
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
        console.log("search val: "+$scope.search);
        if (($scope.search == "@") || ($scope.search == "")) {
            $scope.suggestion_list = [];
            return;
        }
        
        $http.get("/twitter/search/"+$scope.search)
        .then(function(response) {
            $scope.suggestion_list = response.handles;
        });
        
    }
    
    /*
     *if(search_string_val != jq('#search_text').val()){
            search_string_val = jq('#search_text').val();
            if ((search_string_val == "@")||(search_string_val == "")) {
              jq('#open-handle-list').html("");
              jq('#button-container').html("");
              jq('#nothing').show();
              jq('#p-tweet-container').hide();
              return;
            }
            jq(document).getJSON("/twitter/search/"+search_string_val, function(result){
              if (result.search == jq('#search_text').val()) {
                var list_of_suggestions_html = "";
                var text_match = ""; */

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
        var cat_name = ""
        if (($scope.selected_secondary_index != -1) &&($scope.selected_third_index != -1)){
            cat_name = String($scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children[$scope.selected_third_index].name);
        }else if ($scope.selected_secondary_index != -1) {
            cat_name = String($scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name);
        }else {
            cat_name= String($scope.category_structure[$scope.selected_top_index].name);
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
    
});
