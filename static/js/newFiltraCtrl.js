app.controller("newFiltraCtrl", function($scope, $http, $sce, $window) {
    $scope.logged_in = false;
    $scope.username = "";
    
    
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    $scope.current_path = [];
    $scope.time_frames = [{seconds:900, text:"Past 15 Minutes"}, {seconds:3600, text:"Past Hour"},
                           {seconds:10800, text:"Past 3 Hours"}, {seconds:43200, text:"Today"}];
    $scope.selected_time = 1;
    $scope.tweet_array = [];
    $scope.handle_list = [];
    $scope.peer_categories = [];
    
    
    $http.get("/api/category")
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
    
    
    $scope.redirectHome = function(){
        if( (typeof tracking == 'undefined')){
            document.location = "/";
        }else{
            document.location = "/?tracking=0"
        }
    }
    
    $scope.selectionChange = function(top, second, third) {
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        reloadCurrentPath();
        loadTweets();
        loadHandles();
    }
    
    
    
    
    //PRIVATE METHODS
    
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
    
    
    
});
