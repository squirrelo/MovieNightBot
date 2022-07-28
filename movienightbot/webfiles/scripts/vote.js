Vote = {}

Vote.shouldRedraw = false;
Vote.totalScore = 0;
Vote.lastData = null;
Vote.segmentColors = [ 
	"#FF5E71","#A95EFF","#5EA6FF","#5EFFB6","#8E3A3A",
	"#5E6BFF","#EEFF5E","#608E3A","#3B7493","#8D963C",
	"#DEFF5E","#793B91"
];
Vote.refreshCount = 0;
Vote.maxRefreshCount = 30;
Vote.timeoutms = 1000 * 30;

Vote.Init = function() {
	//Get initial vote data, then do something with it!
	window.onresize = Vote.OnResize;
	this.RequestData();
}

Vote.RequestData = function() {
	let xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			Vote.RequestFulfilled(this.responseText);
		}
	}

	let request = "/json/vote?server=" + Utility.GetQueryValue('server');
	
	xhttp.open("GET", request, true);
	xhttp.send();
}

Vote.RequestFulfilled = function(responseText) {
	let parsed = {};
	try {
		parsed = JSON.parse(responseText)
	} catch {
		return;
	}

	this.lastData = parsed;
	this.RenderVoteData()

	let moviesList = document.querySelector(".movieList");
	moviesList.innerHTML = "";

	if (this.lastData == null || this.lastData.movies.length == 0) {
		moviesList.innerHTML = "Nothing right now.";
		return;
	}

	for (let i = 0; i < this.lastData.movies.length; i++) {
		let movie = this.lastData.movies[i];
		let color = "#fff";
		if (i < this.segmentColors.length)
			color = this.segmentColors[i];

		let item = new MovieVote(movie, color);
		item.Init();
		moviesList.appendChild(item.domObject);
	}

	if (this.lastData.voter_count < 1)
		document.querySelector("#voteCount").innerHTML = "Participants: None";
	else
		document.querySelector("#voteCount").innerHTML = "Participants: " + this.lastData.voter_count


	if (this.refreshCount < this.maxRefreshCount) {
		setTimeout(function() {Vote.RequestData()}, Vote.timeoutms);
		this.refreshCount ++;
	} else {
		document.querySelector("#warning").innerHTML = "Automatic refresh timed out, please refresh page.";
	}
}

Vote.RenderVoteData = function() {
	this.shouldRedraw = true;
	this.totalScore = 0;
	for (let i = 0; i < this.lastData.movies.length; i++) {
		this.totalScore += this.lastData.movies[i].score;
	}
}

Vote.DrawChart = function(p) {
	this.shouldRedraw = false;
	p.background('#263D59');
	p.noStroke();

	if (this.lastData == null) {
		p.fill('#fff');
		p.textSize(p.width * 0.03);
		p.textAlign(p.CENTER);
		p.text("No Data Yet", p.width * 0.5, p.width * 0.5);
		return
	}

	if (this.lastData.movies.length == 0) {
		p.fill('#555');
		p.circle(p.width*0.5, p.height*0.5, p.width);
		p.fill('#fff');
		p.textSize(p.width * 0.03);
		p.textAlign(p.CENTER);
		p.text("No Ongoing Vote", p.width * 0.5, p.width * 0.5);
		return;		
	}

	if (this.totalScore <= 0) {
		p.fill('#555');
		p.circle(p.width*0.5, p.height*0.5, p.width);
		p.fill('#fff');
		p.textSize(p.width * 0.03);
		p.textAlign(p.CENTER);
		p.text("No Votes Yet", p.width * 0.5, p.width * 0.5);
		return;
	}
	
	//Render the movies with specified colors.
	let lastAngle = 0;
	for (let i = 0; i < this.lastData.movies.length; i++) {
		let movie = this.lastData.movies[i];
		if (movie.score == 0)
			continue;

		let arcLength = (movie.score / this.totalScore) * p.TWO_PI;
		let col = p.color(p.random(255), p.random(255), p.random(255));
		if (i < this.segmentColors.length)
			col = p.color(this.segmentColors[i]);

		p.fill(col);
		p.arc(p.width * 0.5, p.width * 0.5, p.width, p.width, lastAngle, lastAngle + arcLength);
		lastAngle += arcLength;
	}

	lastAngle = 0;
	let radiusPercent = 0.35;
	for (let i = 0; i < this.lastData.movies.length; i++) {
		let movie = this.lastData.movies[i];
		if (movie.score == 0)
			continue;
		let arcLength = (movie.score / this.totalScore) * p.TWO_PI;
		let textAngle = ((lastAngle + arcLength) - lastAngle) * 0.5 + lastAngle;
		p.fill('#000')
		p.textSize(p.width * 0.03);
		p.textAlign(p.CENTER);
		p.text(movie.title, p.width * 0.5 + p.cos(textAngle) * p.width * radiusPercent, p.width * 0.5 + p.sin(textAngle) * p.width * radiusPercent);
		p.text(movie.score, p.width * 0.5 + p.cos(textAngle) * p.width * radiusPercent * 0.5, p.width * 0.5 + p.sin(textAngle) * p.width * radiusPercent * 0.5);
		lastAngle += arcLength;
	}
}

Vote.ShowSuggested = function() {
	window.location.href = "/movies.html?server=" + Utility.GetQueryValue('server') + "&view=suggested";
}

Vote.ShowWatched = function() {
	window.location.href = "/movies.html?server=" + Utility.GetQueryValue('server') + "&view=watched";
}

const p5Setup = ( p ) => {

	this.canvas = null;

	p.setup = function() {
		this.canvas = p.createCanvas(window.innerWidth * 0.5, window.innerWidth * 0.5);
		p.windowResized();
	}

	p.draw = function() {
		if (!Vote.shouldRedraw)
			return;
		Vote.DrawChart(p);
	}

	p.windowResized = function() {
		let size = window.innerWidth;
		if (window.innerHeight < window.innerWidth)
			size = window.innerHeight;
		
		size *= 0.5;

		p.resizeCanvas(size, size);
		Vote.shouldRedraw = true;
	}
}

canvasEnvironment = new p5(p5Setup, 'piechart');

function MovieVote(movieJSON, legendColor) {
	this.suggestionJSON = movieJSON;
	this.domObject = null;
	this.baseObj = null;

	this.Init = function() {
		this.baseObj = new SuggestedMovie(this.suggestionJSON);
		this.baseObj.Init(movieJSON);
		this.domObject = this.baseObj.domObject;
		console.log(this.domObject);

		//Modify the base object to show the legend color
		let data2 = this.domObject.querySelector("#data2");
		data2.innerHTML = "<h3>Chart Color</h3>";
		data2.style.backgroundColor = legendColor;
	}
}


Vote.Init();