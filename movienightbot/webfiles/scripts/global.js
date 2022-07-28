Utility = {};

Utility.CharIsNumber = function(char) {
	return char == '0' || char == '1' || char == '2' || char == '3' || char == '4' || char == '5' || char == '6' || char == '7' || char == '8' || char == '9';
}


Utility.GetQueryValue = function(key) {
	var value = "";
	var queryString = window.location.search;
	if (queryString) {
		params = new URLSearchParams(queryString);
		if (params) {
			value = params.get(key);
		}
	}

	return value;
}

Mathf = {};

Mathf.Lerp = function(value1, value2, a) {
	return value1 + (value2 - value1) * a;
}

Mathf.LerpClamped = function(value1, value2, a) {
	a = a < 0 ? 0 : a;
	a = a > 1 ? 1 : a;
	return value1 + (value2 - value1) * a;
}


function Vector3(x, y, z) {
	this.x = x;
	this.y = y;
	this.z = z;

	this.Set = function(x, y, z) {
		this.x = x;
		this.y = y;
		this.z = z;
	}

	this.Add = function(other) {
		this.x += other.x;
		this.y += other.y;
		this.z += other.z;
	}

	this.Lerp = function(vector1, vector2, a) {
		let newVector = new Vector3();
		newVector.x = Math2.Lerp(vector1.x, vector2.x, a);
		newVector.y = Math2.Lerp(vector1.y, vector2.y, a);
		newVector.z = Math2.Lerp(vector1.z, vector2.z, a);
		return newVector;
	}

	this.Scale = function(scalar) {
		this.x *= scalar;
		this.y *= scalar;
		this.z *= scalar;
	}

	this.RGB = function() {
		return "rgb(" + this.x + "," + this.y + "," + this.z + ")";
	}

	this.ToString = function() {
		return "(" + this.x + "," + this.y + "," + this.z + ")";
	}
}

function SuggestedMovie(suggestionJSON) {

	this.suggestionJSON = suggestionJSON;
	this.domObject = null;

	this.Init = function() {
		this.domObject = document.createElement('div');
		let htmlText = '<div id="image"><img id="imgCover" class="coverImage" src="/content/images/loading.gif" /><h2 id="txtYear"></h2></div>';
		htmlText += '<div id="imdbData" class="imdbData"><a id="imdbLink" href="" target="#"><h2 id="txtTitle"></h2></a></div>';
		htmlText += '<div id="genres" class="genres"><ul></ul></h2></div>';
		htmlText += '<div id="data1"><p id="txtSuggestor"></p><p id="txtSuggestDate"></p></div>';
		htmlText += '<div id="data2" class="data2"><p id="txtTotalVotes"></p><p id="txtTotalScore"></p></p><p id="txtVoteEvents"></div>';
		this.domObject.innerHTML = htmlText;

		this.domObject.classList.add("item");

		let imgCover = this.domObject.querySelector("#imgCover");
		imgCover.onload = function() {
			if (this.src !== this.getAttribute("data-src"))
				this.src = this.getAttribute("data-src");
		}
		if (this.suggestionJSON.full_size_poster_url != null)
			imgCover.setAttribute("data-src", this.suggestionJSON.full_size_poster_url);
		else
			imgCover.setAttribute("data-src", "/content/images/movienotfound.png");

		this.domObject.querySelector("#txtTitle").innerHTML = this.suggestionJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.suggestionJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.suggestionJSON.suggestor;
		let suggestDate = new Date(this.suggestionJSON.date_suggested);
		this.domObject.querySelector("#txtSuggestDate").innerHTML = "Suggested On: " + suggestDate.toLocaleDateString();
		this.domObject.querySelector("#txtTotalVotes").innerHTML = "Total Votes: " + this.suggestionJSON.total_votes;
		this.domObject.querySelector("#txtTotalScore").innerHTML = "Total Score: " + this.suggestionJSON.total_score;
		this.domObject.querySelector("#txtVoteEvents").innerHTML = "Vote Events Entered: " + this.suggestionJSON.num_votes_entered;

		if (this.suggestionJSON.imdb_id != null)
			this.domObject.querySelector("#imdbLink").href = "https://www.imdb.com/title/tt" + this.suggestionJSON.imdb_id;
		else
			this.domObject.querySelector("#imdbLink").href = "#";

		if (this.suggestionJSON.genre && this.suggestionJSON.genre.length > 0) {
			let ul = this.domObject.querySelector("#genres ul");
			for (let i = 0; i < this.suggestionJSON.genre.length; i++) {
				let element = document.createElement("li");
				element.innerHTML = this.suggestionJSON.genre[i];
				ul.appendChild(element);
			}
		}
	}
}

function WatchedMovie(watchedJSON) {
	this.watchedJSON = watchedJSON;
	this.domObject = null;

	this.Init = function() {
		this.domObject = document.createElement('div');
		let htmlText = '<div id="image"><img id="imgCover" class="coverImage" src="/content/images/loading.gif" /><h2 id="txtYear"></h2></div>';
		htmlText += '<div id="imdbData" class="imdbData"><a id="imdbLink" href="" target="#"><h2 id="txtTitle"></h2></a></div>';
		htmlText += '<div id="genres" class="genres"><ul></ul></h2></div>';
		htmlText += '<div id="data1"><p id="txtSuggestor"><p id="txtSuggestDate"></p></p><p id="txtWatchDate"></p></div>';
		htmlText += '<div id="data2" class="data2"><p id="txtTotalVotes"></p><p id="txtTotalScore"></p><p id="txtVoteEvents"></p></div>';
		this.domObject.innerHTML = htmlText;

		this.domObject.classList.add("item");

		let imgCover = this.domObject.querySelector("#imgCover");
		imgCover.onload = function() {
			if (this.src !== this.getAttribute("data-src"))
				this.src = this.getAttribute("data-src");
		}
		if (this.watchedJSON.full_size_poster_url != null)
			imgCover.setAttribute("data-src", this.watchedJSON.full_size_poster_url);
		else
			imgCover.setAttribute("data-src", "/content/images/movienotfound.png");

		this.domObject.querySelector("#txtTitle").innerHTML = this.watchedJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.watchedJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.watchedJSON.suggestor;
		let suggestDate = new Date(this.watchedJSON.date_suggested);
		let watchDate = new Date(this.watchedJSON.date_watched);
		this.domObject.querySelector("#txtSuggestDate").innerHTML = "Suggested On: " + suggestDate.toLocaleDateString();
		this.domObject.querySelector("#txtWatchDate").innerHTML = "Watched On: " + watchDate.toLocaleDateString();
		this.domObject.querySelector("#txtTotalVotes").innerHTML = "Total Votes: " + this.watchedJSON.total_votes;
		this.domObject.querySelector("#txtTotalScore").innerHTML = "Total Score: " + this.watchedJSON.total_score;
		this.domObject.querySelector("#txtVoteEvents").innerHTML = "Vote Events Entered: " + this.watchedJSON.num_votes_entered;
		if (this.watchedJSON.imdb_id != null)
			this.domObject.querySelector("#imdbLink").href = "https://www.imdb.com/title/tt" + this.watchedJSON.imdb_id;
		else
			this.domObject.querySelector("#imdbLink").href = "#";

		if (this.watchedJSON.genre && this.watchedJSON.genre.length > 0) {
			let ul = this.domObject.querySelector("#genres ul");
			for (let i = 0; i < this.watchedJSON.genre.length; i++) {
				let element = document.createElement("li");
				element.innerHTML = this.watchedJSON.genre[i];
				ul.appendChild(element);
			}
		}
	}
} 