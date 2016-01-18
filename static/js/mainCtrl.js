app.controller("mainCtrl", function($scope, $http, $sce, $window) {
    $scope.category_structure = [];
    
    $scope.display_sections = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        loadTweets();
        
    });
    
    
    
    
    
    
    //private methods
    function loadTweets(){
        $scope.display_sections = [];
        //first iterate through category structure
        for(i=0; i<$scope.category_structure.length; i++){
            //now what does the
            var cat = $scope.category_structure[i];
            var endPoint = "/api/reader/"+cat.name+"/size/4/time/3600";
            console.log("fetching from: "+endPoint);
            $http.get(endPoint)
            .then(function(response) {
                $scope.display_sections.append({"category": cat, "tweets":response.data});
                console.log("display sections: "+$scope.display_sections);
            });
        }
        
        
        
    }
});