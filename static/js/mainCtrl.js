app.controller("mainCtrl", function($scope, $http, $sce, $window) {
    $scope.category_structure = [];
    
    $scope.tweet_sections = [];
    
    $scope.display_sections = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        loadTweets();
        
    });
    
    
    
    
    
    
    //private methods
    function loadTweets(){
        $scope.tweet_sections = [];
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
                $scope.tweet_sections.push({"category": cat, "tweets":response.data});
                console.log("display sections: "+$scope.tweet_sections);
                if (completion_count  == ($scope.category_structure.length) ) {
                    for (j = 0; j<$scope.tweet_sections.length; j++) {
                        console.log("section: "+$scope.tweet_sections[j].name);
                    }
                    $scope.tweet_sections.sort(compare);
                    for (j = 0; j<$scope.tweet_sections.length; j++) {
                        console.log("section: "+$scope.tweet_sections[j].name);
                    }
                }
            });
        }
    }
    

    
    function compare(a,b) {
        a_total = 0;
        b_total = 0;
        for (i=0; i<a["tweets"].length; i++){
            a_total += a["tweets"][i].tweet_count;
        }
        
        for(i =0; i<b["tweets"].length; i++){
            b_total += b["tweets"][i].tweet_count;
        }
        
        if (a_total < b_total)
          return -1;
        else if (a_total > b_total)
          return 1;
        else 
          return 0;
      }
});