app.controller("mainCtrl", function($scope, $http, $sce, $window) {
    $scope.category_structure = [];
    
    $scope.tweet_sections = [];
    
    $scope.all_tweets = [];
    
    $http.get("/category")
    .then(function(response) {
        $scope.category_structure = response.data;
        loadTweets();
        
    });
    
    $scope.convertSecondsToDeltaTime = function(seconds){
        if (seconds < 60) {
            return seconds+" sec";
        } else if (seconds < 3600) {
            var minutes = Math.round( seconds / 60);
            return minutes +" min";
        } else{
            var hours = Math.round( seconds / 3600);
            return hours + " hours";
        }
    }
    
    
    //private stuff
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
            for(i=0; i<response.data.length; i++){
                tweet = response.data[i];
                $scope.all_tweets.push(tweet);
            }
            if (completion_count  == ($scope.category_structure.length) ) {
                $scope.tweet_sections.sort(compareSections);
                $scope.all_tweets.sort(compareTweets);
            }
        });
    }
    //({category: Sports, tweets: [{tweet1}, {tweet2}]}, {category: Regional, tweets: [{tweet1}, {tweet2}]})

    
    function compareTweets(a, b) {
        if (a.tweet_count > b.tweet_count) {
            return -1;
        }else if (b.tweet_count > a.tweet_count) {
            return 1;
        } else{
            return 0;
        }
        
    }
    function compareSections(a,b) {
        a_total = 0;
        b_total = 0;
        for (i=0; i<a["tweets"].length; i++){
            a_total += a["tweets"][i].tweet_count;
        }
        
        for(i =0; i<b["tweets"].length; i++){
            b_total += b["tweets"][i].tweet_count;
        }
        
        if (a_total > b_total)
          return -1;
        else if (a_total < b_total)
          return 1;
        else 
          return 0;
      }
});