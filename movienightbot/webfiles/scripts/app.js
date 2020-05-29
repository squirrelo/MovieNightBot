
var suggestionsRequest = "/dev/movienightbot/testData.json";

var app = new MovieNightBot();
var settings = new Settings();

function MovieNightBot() {

	this.items = null;
	this.txtPositionP = null;

	this.lastData = null;

	this.bGetSuggested = false;
	this.currentPage = 0;
	this.pageCount = 0;
	this.maxHealth = 0;

	this.healthRed = new Vector3();
	this.healthGreen = new Vector3();

	this.Init = function() {

		this.healthRed.Set(0.7, 0.0, 0.1);
		this.healthGreen.Set(0.0, 0.5, 0.2);

		this.items = document.querySelector("#Items");
		this.txtPositionP = document.querySelector("#PageControls > #Position > p");
		let btnSettingText = document.querySelector("#PageControls > #BtnSetting > p");
		let txtPageTitle = document.querySelector("#TxtPageTitle");

		if (window.location.href.includes("suggested")) {
			this.bGetSuggested = true;
			btnSettingText.innerHTML = "Show Watched";
			txtPageTitle.innerHTML = "Movie Night Bot Suggested Movies";
		} else {
			this.bGetSuggested = false;
			btnSettingText.innerHTML = "Show Suggested";
			txtPageTitle.innerHTML = "Movie Night Bot Watched Movies";
		}

		document.querySelector("#PageControls > #BtnSetting").onclick = this.OnClickBtnSetting;
		document.querySelector("#PageControls > #BtnFirst").onclick = this.OnClickBtnFirst;
		document.querySelector("#PageControls > #BtnPrevious").onclick = this.OnClickBtnPrevious;
		document.querySelector("#PageControls > #BtnNext").onclick = this.OnClickBtnNext;
		document.querySelector("#PageControls > #BtnLast").onclick = this.OnClicBtnLast;

		this.RequestItems();
	}

	this.RequestItems = function() {
		let xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				app.lastData = JSON.parse(this.responseText);
				app.RefreshItems();
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

	this.RefreshItems = function() {
		let highest = 0.0;
		let itemsArray = null;
		if (this.bGetSuggested) {
			itemsArray = this.lastData.suggested;
		} else {
			itemsArray = this.lastData.watched;
		}

		for (let i = 0; i < itemsArray.length; i++) {
			let item = itemsArray;

			if (item.num_votes_entered != 0)
				item.health = (item.total_votes * item.total_score) / item.num_votes_entered;
			else
				item.health = 0;

			highest = Math.max(highest, item.health);
		}

		this.maxHealth = highest;

		this.pageCount = Math.ceil(itemsArray.length / settings.itemsPerPage);
		this.currentPage = 0;
		this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
		this.LoadItems();
	}

	this.LoadItems = function() {
		this.items.innerHTML = "";
		let itemsArray = null;
		if (this.bGetSuggested) {
			itemsArray = this.lastData.suggested;
		} else {
			itemsArray = this.lastData.watched;
		}
		
		for (let i = this.currentPage * settings.itemsPerPage; i < this.currentPage * settings.itemsPerPage + settings.itemsPerPage; i++) {
			if (i >= itemsArray.length)
				break;
			
			let item = null;

			if (this.bGetSuggested)
				item = new SuggestedMovie(itemsArray[i]);
			else
				item = new WatchedMovie(itemsArray[i]);

			item.Init();
			this.items.appendChild(item.domObject);
		}
	}

	this.OnClickBtnFirst = function() {
		if (app.currentPage != 0) {
			app.currentPage = 0;
			app.txtPositionP.innerHTML = app.currentPage + 1 + " of " + app.pageCount;
			app.LoadItems();
		}
	}

	this.OnClickBtnPrevious = function() {
		if (app.currentPage > 0) {
			app.currentPage -= 1;
			app.txtPositionP.innerHTML = app.currentPage + 1 + " of " + app.pageCount;
			app.LoadItems();
		}
	}

	this.OnClickBtnNext = function() {
		if (app.currentPage < app.pageCount-1) {
			app.currentPage += 1;
			app.txtPositionP.innerHTML = app.currentPage + 1 + " of " + app.pageCount;
			app.LoadItems();
		}
	}

	this.OnClicBtnLast = function() {
		if (app.currentPage != app.pageCount -1) {
			app.currentPage = app.pageCount-1;
			app.txtPositionP.innerHTML = app.currentPage + 1 + " of " + app.pageCount;
			app.LoadItems();
		}
	}

	this.OnClickBtnSetting = function() {
		let newURL = window.location.href;
		if (app.bGetSuggested) {
			window.location.href = newURL.replace("suggested", "watched");
		} else {
			window.location.href = newURL.replace("watched", "suggested");
		}
	}
}

function SuggestedMovie(suggestionJSON) {

	this.suggestionJSON = suggestionJSON;
	this.domObject = null;

	this.Init = function() {
		this.domObject = document.createElement('div');
		let htmlText = '<div id="image"><img id="cover" src="../static/content/images/movienotfound.png" /></div>'
		htmlText += '<div id="imdbData"><a id="imdbLink" href=""><h2 id="txtTitle"></h2></a><h2 id="txtYear"></h2></div>';
		htmlText += '<div id="data1"><p id="txtSuggestor"></p><p id="txtSuggestDate"></p></div>';
		htmlText += '<div id="data2"><p id="txtTotalVotes"></p><p id="txtTotalScore"></p></p><p id="txtVoteEvents"></div>';
		htmlText += '<div id="health"><div id="background"><div id="bar">100%</div></div></div>'
		this.domObject.innerHTML = htmlText;

		this.domObject.classList.add("item");
		if (this.suggestionJSON.full_size_poster_url != null)
			this.domObject.querySelector("#cover").src = this.suggestionJSON.full_size_poster_url;

		this.domObject.querySelector("#txtTitle").innerHTML = this.suggestionJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.suggestionJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.suggestionJSON.suggestor;
		let suggestDate = new Date(this.suggestionJSON.date_suggested);
		this.domObject.querySelector("#txtSuggestDate").innerHTML = "Suggested On: " + suggestDate.toLocaleDateString();
		this.domObject.querySelector("#txtTotalVotes").innerHTML = "Total Votes: " + this.suggestionJSON.total_votes;
		this.domObject.querySelector("#txtTotalScore").innerHTML = "Total Score: " + this.suggestionJSON.total_score;
		this.domObject.querySelector("#txtVoteEvents").innerHTML = "Vote Events Entered: " + this.suggestionJSON.num_votes_entered;
		let bar = this.domObject.querySelector("#bar");

		let healthPercentOfMaximum = 0;
		if (app.maxHealth != 0 && !isNaN(app.maxHealth))
			healthPercentOfMaximum = Math.round((this.suggestionJSON.health / app.maxHealth) * 100);

		bar.innerHTML = healthPercentOfMaximum + "%";
		bar.style.width = healthPercentOfMaximum + "%";
		let color = sVector3.Lerp(app.healthRed, app.healthGreen, healthPercentOfMaximum / 100.0);
		
		bar.style.backgroundColor = color.RGB();
		if (this.suggestionJSON.imdb_id != null)
			this.domObject.querySelector("#imdbLink").href = "https://www.imdb.com/title/tt" + this.suggestionJSON.imdb_id;
		else
			this.domObject.querySelector("#imdbLink").href = "#";
	}
}

function WatchedMovie(watchedJSON) {
	this.watchedJSON = watchedJSON;
	this.domObject = null;

	this.Init = function() {
		this.domObject = document.createElement('div');
		let htmlText = '<div id="image"><img id="cover" src="../static/content/images/movienotfound.png" /></div>'
		htmlText += '<div id="imdbData"><a id="imdbLink" href=""><h2 id="txtTitle"></h2></a><h2 id="txtYear"></h2></div>';
		htmlText += '<div id="data1"><p id="txtSuggestor"></p><p id="txtWatchDate"></p></div>';
		htmlText += '<div id="data2"><p id="txtTotalVotes"></p><p id="txtTotalScore"></p><p id="txtVoteEvents"></p></div>';
		this.domObject.innerHTML = htmlText;

		this.domObject.classList.add("item");

		if (this.watchedJSON.full_size_poster_url != null)
			this.domObject.querySelector("#cover").src = this.watchedJSON.full_size_poster_url;
		this.domObject.querySelector("#txtTitle").innerHTML = this.watchedJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.watchedJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.watchedJSON.suggestor;
		let suggestDate = new Date(this.watchedJSON.date_watched);
		this.domObject.querySelector("#txtWatchDate").innerHTML = "Watched On: " + suggestDate.toLocaleDateString();
		this.domObject.querySelector("#txtTotalVotes").innerHTML = "Total Votes: " + this.watchedJSON.total_votes;
		this.domObject.querySelector("#txtTotalScore").innerHTML = "Total Score: " + this.watchedJSON.total_score;
		this.domObject.querySelector("#txtVoteEvents").innerHTML = "Vote Events Entered: " + this.watchedJSON.num_votes_entered;
		if (this.watchedJSON.imdb_id != null)
			this.domObject.querySelector("#imdbLink").href = "https://www.imdb.com/title/tt" + this.watchedJSON.imdb_id;
		else
			this.domObject.querySelector("#imdbLink").href = "#";
	}
} 

function Settings() {
	this.itemsPerPage = 10;
}