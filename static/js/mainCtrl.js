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
        var completion_count = 0;
        for(i=0; i<$scope.category_structure.length; i++){
            //now what does the
            var cat = $scope.category_structure[i];
            var endPoint = "/api/reader/"+cat.name+"/size/4/time/3600";
            console.log("fetching from: "+endPoint);
            $http.get(endPoint)
            .then(function(response) {
                completion_count++;
                $scope.display_sections.push({"category": cat, "tweets":response.data});
                console.log("display sections: "+$scope.display_sections);
                if (completion_count  == ($scope.category_structure.length-1) ) {
                    console.log("finished loading tweet sections");
                }
            });
        }
        
        
        
    }
});