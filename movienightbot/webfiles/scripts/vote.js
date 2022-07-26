Vote = {}

Vote.Init = function() {
	//Get initial vote data, then do something with it!
	Vote.RequestData();
}

Vote.RequestData = function() {
	let xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			Vote.RequestFulfilled(this.responseText);
		}
	}

	let arr = window.location.href.split("/");
	let request = arr[0] + "//" + arr[2];

	if (this.bGetSuggested)
		request += "/json" + window.location.pathname;
	else
		request += "/json" + window.location.pathname;
	
	xhttp.open("GET", request, true);
	xhttp.send();
}

Vote.RequestFulfilled = function(responseText) {
	let parsed = {};
	try {
		parsed = JSON.parse(responseText)
	} catch {
		//No data loaded, show some kind of error.
		console.log("Json not sent.");
		console.log(responseText);
		return;
	}
	console.log(parsed);
}

Vote.Init();