'use strict';

angular.module('godotApp', ['ngResource','ngRoute','ngMessages'])
.config(function ($routeProvider,$locationProvider){
    $routeProvider.
        when('/home', {
            templateUrl: 'partials/home.html'
        })
        .when('/browse', {
            templateUrl: 'partials/browse.html',
            controller: 'browseData'
        })
        .when('/about', {
            templateUrl: 'partials/about.html'
        })
        .when('/contact', {
            templateUrl: 'partials/contact.html'
        })
        .when('/resources', {
            templateUrl: 'partials/resources.html'
        })
        .when('/get_id', {
            templateUrl: 'partials/get_id.html'
        })
        .when('/id/:id',{
            templateUrl: 'partials/show_id.html',
            controller: 'showGodotId'
        })
        .otherwise({
            redirectTo: '/home' 
        });
        $locationProvider.html5Mode({
          enabled: true
        });
})
.controller("showGodotId", function($scope, $routeParams,$http) {
    $scope.godot_id = $routeParams.id;
    $http.get("index.php?godot_id=" + $scope.godot_id)
    .then(function(response) {
        $scope.godot_id_resultat = response.data;
        $scope.attestations = $scope.godot_id_resultat.data.attestations;
        $scope.calendarInfo = $scope.godot_id_resultat.data.calendar_path[0];
        $scope.calendarPartials = $scope.calendarInfo.calendar_partials;        
    });
})
.controller("browseData", function($scope, $routeParams,$http) {
    $http.get("browse.php")
    .then(function(response) {
        $scope.resultat = response.data.data.calendar_data;
        console.log($scope.resultat);
        
    });
})
;
