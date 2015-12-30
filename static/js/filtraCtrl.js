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
    
    $scope.topIndexChange = function(top) {
        console.log("changing to: "+top);
        console.log("selected top was: "+selected_top_index);
        selected_top_index = top;
    }
});
