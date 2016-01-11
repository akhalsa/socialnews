app.controller("filtraCtrl", function($scope, $http, $sce, $window) {
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
    
    $scope.peer_categories = [];
    $scope.showVotes = false;
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
        if (typeof $scope.category_name != 'undefined' ) {
            starting = checkForCatMatch( $scope.category_name);
            $scope.selected_top_index = starting[0];
            $scope.selected_secondary_index = starting[1];
            $scope.selected_third_index = starting[2];
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles();
        
    });
    if($window.innerWidth > 992){
        $scope.showVotes = true;
    }
    
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
        trackCategorySelection(currentCatName());
        loadTweets();
        loadHandles();
    }
    
    $scope.breadCrumbSubSelect = function(bc_sub_index){
        if  ($scope.selected_secondary_index == -1) { 
            $scope.selected_secondary_index = bc_sub_index;
        } else if ($scope.selected_third_index == -1) {
            $scope.selected_third_index = bc_sub_index;
        }
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    $scope.selectionChange = function(top, second, third) {
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        trackCategorySelection(currentCatName());
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    
    $scope.timeChange = function(new_time_index){
        $scope.selected_time = new_time_index;
        trackTimeRangeSelection($scope.time_frames[new_time_index].seconds)
        loadTweets();
    }
    
    $scope.togglePopup = function(){
        console.log("toggle popup");
        $scope.nomination_visible = !$scope.nomination_visible;
    }
    
    $scope.toggleVotes = function(){
        console.log("flipping");
        $scope.showVotes = !$scope.showVotes;
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
        trackVote(handle_string);
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
            trackNomination($scope.search)
            $http.post( "/handle/"+$scope.search+"/category/"+currentCatName()+"/upvote/"+1).then(function(response) {
                loadHandles();
            });
        }else{
            alert("Please enter a valid twitter handle");
        }
    }
    
    $scope.refreshButton = function(){
        loadTweets();
        console.log("calling refresh");
        trackRefresh();
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
            $scope.peer_categories = $scope.category_structure[$scope.selected_top_index].children;
            
        } else if ($scope.selected_third_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name ];
            $scope.peer_categories = $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children;
        } else{
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].name,
                                   $scope.category_structure[$scope.selected_top_index].children[$scope.selected_secondary_index].children[$scope.selected_third_index].name ]
            $scope.peer_categories = [];
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
            
            $scope.tweet_array = response.data;
            console.log("tweet array length: "+$scope.tweet_array.length);
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
    
    function checkForCatMatch(name) {
        for(i = 0; i<$scope.category_structure.length; i++){
            pos_name = getCatNameWithPositionVals(i, -1, -1);
            if (name.toUpperCase() === pos_name.toUpperCase() ) {
                return [i, -1, -1];
            }
            if (!$scope.category_structure[i].children) {
                continue;
            }
            
            for(j = 0; j<$scope.category_structure[i].children.length; j++){
                pos_name = getCatNameWithPositionVals(i, j, -1);
                if (name.toUpperCase() === pos_name.toUpperCase() ) {
                    return [i, j, -1];
                }
                if (!$scope.category_structure[i].children[j].children) {
                    continue;
                }
                for(k = 0; k < $scope.category_structure[i].children[j].children.length; k++){
                    pos_name = getCatNameWithPositionVals(i, j, k);
                    if (name.toUpperCase() === pos_name.toUpperCase() ) {
                        return [i, j, k];
                    }
                }
            }
        }
        return null;
    }
    
    
    

    // GOOGLE ANALYTICS COPY AND PASTE
    
    
    var tracking = getUrlParameter("tracking");
    if((typeof tracking == 'undefined')){
        ext_string = (window.location.href.indexOf("filtra.io") > -1) ? "1" : "2";
        console.log("setting up with ext string: "+ext_string);
        ga('create', 'UA-70081756-'+ext_string, 'auto');
        $window.ga('send', 'pageview');
    }

        
    var url_time_frame = getUrlParameter("time");
    if (typeof url_time_frame != 'undefined') {
      time_frame_index = url_time_frame;
    }
    
    
    
    function getUrlParameter(sParam) {
      var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;
  
      for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
          return sParameterName[1] === undefined ? true : sParameterName[1];
        }
      }
    }
    
    $scope.trackOutboundPreviewLink = function(url) {
        console.log("calling outbound: "+url);
        if( (typeof tracking == 'undefined')){
            ga('send', 'event', 'outbound-preview', 'click', url, {'hitCallback':
                function () {
                }
            });
        }
       
    }
   
    
    var trackCategorySelection = function(cat_name){
        if((typeof tracking == 'undefined')){
            console.log("triggering a change event with: "+cat_name);
            $window.ga('send', 'event', 'configuration change', 'change category', cat_name, {'hitCallback':
             function () {
             }
           });
        }
    }
    
    var trackVote = function(handle){
      console.log("vote track trigger");
      if( (typeof tracking == 'undefined')){
        $window.ga('send', {
          hitType: 'event',
          eventCategory: 'Vote',
          eventAction: handle
          } );
      }
    }
    
    var trackRefresh = function(){
        console.log("refreshing");
        if( (typeof tracking == 'undefined')){
            console.log("refreshing2");
            $window.ga('send', {
                hitType: 'event',
                eventCategory: 'refresh',
                eventAction: 'refresh',
                eventLabel: 'refresh'
                    });
        }
    }
    
    var trackNomination = function(handle){
      if( (typeof tracking == 'undefined')){
        $window.ga('send', {
          hitType: 'event',
          eventCategory: 'Vote',
          eventAction: 'Nomination',
          eventLabel: handle
          }
        );
      }
    }
    
    var trackTimeRangeSelection = function(seconds){
        if( (typeof tracking == 'undefined')){
            $window.ga('send', 'event', 'configuration change', 'change time frame', seconds, {'hitCallback':
             function () {
             }
           });
        }
    }
});
