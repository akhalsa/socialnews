app.controller("tweetCtrl", function($scope, $http, $sce, $window) {
    $scope.$watch('tweet_id', function () {
        if (typeof $scope.tweet_id != 'undefined' ) {
            console.log($scope.tweet_id);
        }
        
        
    });
});
