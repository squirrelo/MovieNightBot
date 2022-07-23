
var suggestionsRequest = "/dev/movienightbot/testData.json";

var MovieNightBot = new MovieNightBotConstructor();
var Settings = new SettingsConstructor();

function MovieNightBotConstructor() {

	this.items = null;
	this.txtPositionP = null;
	this.txtPositionP2 = null;

	this.lastData = null;

	this.bGetSuggested = false;
	this.currentPage = 0;
	this.pageCount = 0;
	this.maxAverageVotePower = 0;
	this.maxAveragePopularity = 0;

	this.healthRed = new Vector3();
	this.healthGreen = new Vector3();

	this.Init = function() {

		this.healthRed.Set(0.7, 0.0, 0.1);
		this.healthGreen.Set(0.0, 0.5, 0.2);

		this.items = document.querySelector("#Items");
		this.txtPositionP = document.querySelector("#PageControls > #Position > p");
		this.txtPositionP2 = document.querySelector("#PageControls2 > #Position > p");

		let btnSettingText = document.querySelector("#BtnSetting h2");
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

		this.RequestItems();
	}

	this.RequestItems = function() {
		let xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				MovieNightBot.lastData = JSON.parse(this.responseText);
				MovieNightBot.RefreshItems();
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

		this.maxAverageVotePower = 0;
		this.maxAveragePopularity = 0;
		let itemsArray = null;
		let includedLetters = [];

		if (this.bGetSuggested) {
			itemsArray = this.lastData.suggested;
		} else {
			itemsArray = this.lastData.watched;
		}

		for (let i = 0; i < itemsArray.length; i++) {
			let item = itemsArray[i];

			if (item.num_votes_entered != 0 && item.total_score != 0) {
				item.votePower = (item.total_score / item.total_votes) / item.num_votes_entered;
				item.popularity = (item.total_score * item.total_votes) / item.num_votes_entered;
			} else {
				item.votePower = 0;
				item.popularity = 0;
			}

			this.maxAverageVotePower = Math.max(this.maxAverageVotePower, item.votePower);
			this.maxAveragePopularity = Math.max(this.maxAveragePopularity, item.popularity);
			if (Utility.CharIsNumber(item.title.substring(0, 1).toUpperCase()))
				includedLetters.push("#");
			else
				includedLetters.push(item.title.substring(0, 1).toUpperCase());
		}

		this.GenerateLetterNav(includedLetters);
		

		this.pageCount = Math.ceil(itemsArray.length / Settings.itemsPerPage);
		this.currentPage = 0;
		this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
		this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
		this.LoadItems();
	}

	this.GenerateLetterNav = function(included) {
		let letterArray = ["#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
		let letterNavDiv = document.querySelector("#LetterNav");
		letterNavDiv.innerHTML = "";
		for (let i = 0; i < letterArray.length; i++) {
			let nav = document.createElement('div');

			if (included.includes(letterArray[i])) {
				nav.classList.add("Active");
				nav.setAttribute("data-letter", letterArray[i]);
				nav.onclick = this.OnClickBtnLetter.bind(this);
			} else {
				nav.classList.add("Inactive");
			}

			nav.innerHTML = letterArray[i] + "&nbsp;";
			letterNavDiv.appendChild(nav);
		}
	}

	this.LoadItems = function() {
		this.items.innerHTML = "";
		let itemsArray = null;
		if (this.bGetSuggested) {
			itemsArray = this.lastData.suggested;
		} else {
			itemsArray = this.lastData.watched;
		}
		
		for (let i = this.currentPage * Settings.itemsPerPage; i < this.currentPage * Settings.itemsPerPage + Settings.itemsPerPage; i++) {
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
		if (this.currentPage != 0) {
			this.currentPage = 0;
			this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.LoadItems();
		}
	}

	this.OnClickBtnPrevious = function() {
		if (this.currentPage > 0) {
			this.currentPage -= 1;
			this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.LoadItems();
		}
	}

	this.OnClickBtnNext = function() {
		if (this.currentPage < this.pageCount-1) {
			this.currentPage += 1;
			this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.LoadItems();
		}
	}

	this.OnClickBtnLast = function() {
		if (this.currentPage != this.pageCount -1) {
			this.currentPage = this.pageCount-1;
			this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.LoadItems();
		}
	}

	this.OnClickBtnSetting = function() {
		let newURL = window.location.href;
		if (this.bGetSuggested) {
			window.location.href = newURL.replace("suggested", "watched");
		} else {
			window.location.href = newURL.replace("watched", "suggested");
		}
	}

	this.OnClickBtnLetter = function(event) {
		//console.log(event.target.getAttribute("data-letter"));
		let clicked = event.target.getAttribute("data-letter");
		let itemsArray = null;
		let matchChars = [];
		if (clicked == "#")
			matchChars = ["0","1","2","3","4","5","6","7","8","9"];
		else
			matchChars = [clicked];
		if (this.bGetSuggested) {
			itemsArray = this.lastData.suggested;
		} else {
			itemsArray = this.lastData.watched;
		}
		let itemIndex = -1;
		for (let i = 0; i < itemsArray.length; i++) {
			for (let j = 0; j < matchChars.length; j++) {
				let item = itemsArray[i];
				let match = matchChars[j];
				if (item.title != "" && item.title.substring(0, 1).toUpperCase() == match) {
					itemIndex = i;
					break;
				}
			}
			if (itemIndex != -1)
				break;
		}

		if (itemIndex != -1) {
			//Navigate to the appropriate location.
			let targetPage = Math.floor(itemIndex / Settings.itemsPerPage);
			this.currentPage = targetPage;
			this.txtPositionP.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.txtPositionP2.innerHTML = this.currentPage + 1 + " of " + this.pageCount;
			this.LoadItems();
		}

	}
}

function SuggestedMovie(suggestionJSON) {

	this.suggestionJSON = suggestionJSON;
	this.domObject = null;

	this.Init = function() {
		this.domObject = document.createElement('div');
		let htmlText = '<div id="image"><img id="imgCover" class="coverImage" src="../static/content/images/loading.gif" /></div>'
		htmlText += '<div id="imdbData" class="imdbData"><a id="imdbLink" href="" target="#"><h2 id="txtTitle"></h2></a><h2 id="txtYear"></h2></div>';
		htmlText += '<div id="data1"><p id="txtSuggestor"></p><p id="txtSuggestDate"></p></div>';
		htmlText += '<div id="data2" class="data2"><p id="txtTotalVotes"></p><p id="txtTotalScore"></p></p><p id="txtVoteEvents"></div>';
//		htmlText += '<div id="health"><div id="background"><div id="bar">100%</div></div></div>'
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
			imgCover.setAttribute("data-src", "../static/content/images/movienotfound.png");

		this.domObject.querySelector("#txtTitle").innerHTML = this.suggestionJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.suggestionJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.suggestionJSON.suggestor;
		let suggestDate = new Date(this.suggestionJSON.date_suggested);
		this.domObject.querySelector("#txtSuggestDate").innerHTML = "Suggested On: " + suggestDate.toLocaleDateString();
		this.domObject.querySelector("#txtTotalVotes").innerHTML = "Total Votes: " + this.suggestionJSON.total_votes;
		this.domObject.querySelector("#txtTotalScore").innerHTML = "Total Score: " + this.suggestionJSON.total_score;
		this.domObject.querySelector("#txtVoteEvents").innerHTML = "Vote Events Entered: " + this.suggestionJSON.num_votes_entered;
//		let bar = this.domObject.querySelector("#bar");

		let healthPercentOfMaximum = 0;
		if (MovieNightBot.maxAveragePopularity != 0 && !isNaN(MovieNightBot.maxAveragePopularity))
			healthPercentOfMaximum = Math.round((this.suggestionJSON.popularity / MovieNightBot.maxAveragePopularity) * 100);

//		bar.innerHTML = healthPercentOfMaximum + "%";
//		bar.style.width = healthPercentOfMaximum + "%";
//		let color = sVector3.Lerp(MovieNightBot.healthRed, MovieNightBot.healthGreen, healthPercentOfMaximum / 100.0);
//		color.Scale(256);
//		bar.style.backgroundColor = color.RGB();
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
		let htmlText = '<div id="image"><img id="imgCover" class="coverImage" src="../static/content/images/loading.gif" /></div>'
		htmlText += '<div id="imdbData" class="imdbData"><a id="imdbLink" href="" target="#"><h2 id="txtTitle"></h2></a><h2 id="txtYear"></h2></div>';
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
			imgCover.setAttribute("data-src", "../static/content/images/movienotfound.png");

		this.domObject.querySelector("#txtTitle").innerHTML = this.watchedJSON.title;
		this.domObject.querySelector("#txtYear").innerHTML = this.watchedJSON.year;
		this.domObject.querySelector("#txtSuggestor").innerHTML = "Suggested by: " + this.watchedJSON.suggestor;
		let suggestDate = new Date(this.watchedJSON.date_watched);
		this.domObject.querySelector("#txtSuggestDate").innerHTML = "Suggested On: " + suggestDate.toLocaleDateString();
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

function SettingsConstructor() {
	this.itemsPerPage = 10;
}