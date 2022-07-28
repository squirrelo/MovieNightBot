Vote = {}

Vote.shouldRedraw = false;
Vote.totalScore = 0;
Vote.lastData = null;
Vote.segmentColors = [ 
	"#FF5E71","#A95EFF","#5EA6FF","#5EFFB6","#DEFF5E",
	"#5E6BFF","#EEFF5E","#8D963C","#3B7493","#608E3A",
	"#8E3A3A","#793B91"
];

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
		//No data loaded, show some kind of error.
		console.log("Json not sent.");
		console.log(responseText);
		return;
	}

	this.lastData = parsed;
	this.RenderVoteData()
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
		lastAngle += arcLength;
	}
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


Vote.Init();