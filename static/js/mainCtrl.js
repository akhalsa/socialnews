app.controller("mainCtrl", function($scope, $http, $sce, $window) {
    $scope.category_structure = [];
    
    $scope.tweet_sections = [];
    
    $scope.display_sections = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        loadTweets();
        
    });
    
    
    
    
    
    var completion_count;
    //private methods
    function loadTweets(){
        $scope.tweet_sections = [];
        //first iterate through category structure
        completion_count = 0;
        for(i=0; i<$scope.category_structure.length; i++){
            //now what does the
            var category = $scope.category_structure[i];
            loadCategory(category);
        }
    }
    
    
    function loadCategory(category){
        var endPoint = "/api/reader/"+category.name+"/size/4/time/3600";
        console.log("fetching from: "+endPoint);
        $http.get(endPoint)
        .then(function(response) {
            completion_count++;
            section = {"category": category.name, "tweets":response.data};
            console.log(JSON.stringify(section));
            $scope.tweet_sections.push(section);
            if (completion_count  == ($scope.category_structure.length) ) {
                for (j = 0; j<$scope.tweet_sections.length; j++) {
                    console.log("section: "+$scope.tweet_sections[j]["category"]);
                }
                $scope.tweet_sections.sort(compare);
                for (j = 0; j<$scope.tweet_sections.length; j++) {
                    console.log("section: "+$scope.tweet_sections[j]["category"]);
                }
            }
        });
    }
    //({category: Sports, tweets: [{tweet1}, {tweet2}]}, {category: Regional, tweets: [{tweet1}, {tweet2}]})

    
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