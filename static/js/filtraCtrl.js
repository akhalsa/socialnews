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
        $scope.current_path = [$scope.category_structure[$scope.selected_top_index]];
    });
    
    $scope.selectionChange = function(top, second, third) {
        console.log("changing to: "+top);
        console.log("changing to second: "+second);
        console.log("changing to third: "+third);
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        
        if ($scope.selected_secondary_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index]];
            
        } else if ($scope.selected_third_index == -1) {
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index], $scope.category_structure[$scope.selected_secondary_index] ]
        } else{
            $scope.current_path = [$scope.category_structure[$scope.selected_top_index], $scope.category_structure[$scope.selected_secondary_index], $scope.category_structure[$scope.selected_third_index] ]
        }
        console.log($scope.current_path)
        
    }
    
    $scope.timeChange = function(new_time_index){
        $scope.selected_time = new_time_index;
    }
    
});
