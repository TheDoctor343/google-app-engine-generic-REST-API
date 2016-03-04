console.log("read app.js");

var appDependencies = ['ui.bootstrap'];

var app = angular.module('app', appDependencies);

function HomeController($scope, $http) {
	/*Helper functions*/
	
	function formatNum(s) {
		if (s.length == 1) {
			return "0"+s
		} else {
			return s
		}
	}
	
	$scope.formatTime = function (seconds) {
		var hours = Math.floor(seconds/3600);
		var minutes = Math.floor(seconds/60);
		var left_seconds = seconds % 60;

		hours = formatNum(String(hours));
		minutes = formatNum(String(minutes));
		left_seconds = formatNum(String(left_seconds));
		return hours + ":" + minutes + ":" + left_seconds
	}
	
	function prepareTasks(tasks) {
		tasks.forEach(function(task) {
			task.button_state = "Start";

			/*
			 * #GETSOMETHINGWORKING
			 */
			task.current_task = {
				duration : task.current_task_duration,
				note : task.current_task_note
			}
			if (task.current_task_start) {
				task.current_task.start_time = task.current_task_start;
				task.button_state = "Stop";
			}
		});
	}

	function getTasks() {
		// Get this user's tasks
		console.log("user: " + $scope.current_user.email)
		config = {
			method : "get",
			url : '/task',
			params : {
				user_id : $scope.current_user.email
			}
		}
		$http(config).success(function(data, response, headers) {
			console.log(data);
			console.log("Got The Tasks!")
			prepareTasks(data);
			$scope.tasks = data;
			
			//WHY!?
			//$scope.$apply();
		}).error(function(data, response, headers) {
			alert("Could not load tasks for this user");
		});
	}


	$scope.changeState = function(task) {
		if (task.button_state == "Start") {
			task.button_state = "Stop";
			task.current_task.start_time = new Date().getTime();
			
			//SAVE
			var config = {
				method: 'put',
				url: '/task',
				data: {
					key: task.key,
					current_task_start: task.current_task.start_time,
				}
			}
			
			$http(config).success(function () {
				console.log("Saved Start Time")
			}).error(function () {
				console.log("Failed to save start time")
			});
			
		} else {//Stop
			task.button_state = "Start";
			var current_ms = task.current_task.start_time
			var now = new Date().getTime()

			var diff_ms = now - current_ms

			var diff_s = diff_ms / 1000;

			var new_duration = task.current_task.duration + Math.round(diff_s);
			console.log(new_duration)
			current = task.current_task.start_time
			task.current_task.duration = new_duration;
			
			//SAVE TO DB
			
			var config = {
				method: 'put',
				url: '/task',
				data: {
					key: task.key,
					current_task_duration: task.current_task.duration,
					current_task_start: 0 //So we need to save the fact that the timer was stopped
				}
			}
			$http(config).success(function () {
				console.log("Successfully saved durationS")
			}).error(function () {
				alert("Could not save duration");
			})

		}
	}

	$scope.newTask = function() {
		$scope.modal = true;

	}

	$scope.submitNewTask = function() {

		if ($scope.project_name && $scope.task_name && $scope.task_note) {
			console.log($scope.project_name)

			var duration = 0;

			if ($scope.duration) {
				console.log( typeof ($scope.duration))
				duration = $scope.duration;
			}

			var data = {
				user_id : $scope.current_user.email,
				project_name : $scope.project_name,
				task_name : $scope.task_name,
				current_task_note : $scope.task_note,
				current_task_duration : duration
			}

			var config = {
				method : 'post',
				url : '/task',
				data : data
			}

			$http(config).success(function(data, response, headers) {
				console.log("Saved Task");
				
				//refresh data
				getTasks()

				$scope.modal = false;
			}).error(function() {
				alert("Could not Save task")
			});
		} else {
			$scope.missingfields = true;
		}
	}
	//Init Stuff
	$scope.modal = false;
	$scope.missingfields = false;

	//This is example dat
	var example_tasks = [{
		task_name : "Example",
		user_id : "Wesley",
		project_name : "Some Project",
		current_task : {
			duration : 5.0,
			start_time : "",
			note : "I'm the current task"
		}

	}]

	$scope.current_user = null;

	//Get the current user:
	var config = {
		method : 'get',
		url : '/user',
	}
	$http(config).success(function(data, response, headers) {

		$scope.current_user = data
		console.log(data)
		console.log($scope.current_user)

		// Get this user's tasks
		getTasks();
	}).error(function() {
		alert("Could not get current user");
	});

}


angular.module('app').controller('HomeController', HomeController);
