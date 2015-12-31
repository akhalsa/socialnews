app.controller("filtraCtrl", function($scope, $http) {
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        for (index = 0; index < response.data.length; ++index) {
            console.log(response.data[index].name);
        }
    });
    
    $scope.selectionChange = function(top, second, third) {
        console.log("changing to: "+top);
        console.log("changing to second: "+second);
        console.log("changing to third: "+third);
        $scope.selected_top_index = top;
        $scope.selected_secondary_index = second;
        $scope.selected_third_index = third;
        
        console.log("children length: "+$scope.category_structure[selected_top_index].children[selected_secondary_index].children.length);
    }
});
