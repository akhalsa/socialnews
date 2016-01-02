app.controller("filtraCtrl", function($scope, $http) {
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    $scope.current_path = [];
    $scope.time_frames = [{seconds:900, text:"Past 15 Minutes"}, {seconds:3600, text:"Past Hour"},
                           {seconds:10800, text:"Past 3 Hours"}, {seconds:43200, text:"Today"}];
    $scope.selected_time = 0;
    
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
        reloadCurrentPath();
        loadTweets();
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
    }
    
    
    $scope.timeChange = function(new_time_index){
        $scope.selected_time = new_time_index;
        loadTweets();
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
        var stringName = "/reader/"+currentCatName()+"/time/"+$scope.time_frames[$scope.selected_time].seconds;
        $http.get("/reader/"+currentCatName()+"/time/"+$scope.time_frames[$scope.selected_time].seconds)
        .then(function(response) {
            console.log("got a response");
        });
            
    }
    
});
