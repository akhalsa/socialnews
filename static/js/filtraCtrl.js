app.controller("filtraCtrl", function($scope, $http) {
    $scope.selected_top_index = 0;
    $scope.selected_secondary_index = -1;
    $scope.selected_third_index = -1;
    $scope.category_structure = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        console.log("data is: "+response.data);
    });
});
