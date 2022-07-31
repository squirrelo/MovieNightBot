var suggestionsRequest="/dev/movienightbot/testData.json",MovieNightBot=new MovieNightBotConstructor,Settings=new SettingsConstructor;function MovieNightBotConstructor(){this.items=null,this.txtPositionP=null,this.txtPositionP2=null,this.lastData=null,this.bGetSuggested=!1,this.currentPage=0,this.pageCount=0,this.maxAverageVotePower=0,this.maxAveragePopularity=0,this.Init=function(){this.items=document.querySelector("#Items"),this.txtPositionP=document.querySelector("#PageControls > #Position > p"),this.txtPositionP2=document.querySelector("#PageControls2 > #Position > p");let t=document.querySelector("#BtnSetting h2"),e=document.querySelector("#TxtPageTitle");window.location.href.includes("suggested")?(this.bGetSuggested=!0,t.innerHTML="Show Watched",e.innerHTML="Movie Night Bot Suggested Movies",document.querySelector("#BtnSortByWatchDate").classList.add("hidden")):(this.bGetSuggested=!1,t.innerHTML="Show Suggested",e.innerHTML="Movie Night Bot Watched Movies",document.querySelector("#BtnSortByWatchDate").classList.remove("hidden")),this.RequestItems()},this.RequestItems=function(){let t=new XMLHttpRequest;t.onreadystatechange=function(){4==this.readyState&&200==this.status&&(MovieNightBot.lastData=JSON.parse(this.responseText),MovieNightBot.RefreshItems())};let e="/json/"+Utility.GetQueryValue("view")+"?server="+Utility.GetQueryValue("server");console.log(e),t.open("GET",e,!0),t.send()},this.RefreshItems=function(){this.maxAverageVotePower=0,this.maxAveragePopularity=0;let t=null,e=[];t=this.bGetSuggested?this.lastData.suggested:this.lastData.watched;for(let s=0;s<t.length;s++){let i=t[s];0!=i.num_votes_entered&&0!=i.total_score?(i.votePower=i.total_score/i.total_votes/i.num_votes_entered,i.popularity=i.total_score*i.total_votes/i.num_votes_entered):(i.votePower=0,i.popularity=0),this.maxAverageVotePower=Math.max(this.maxAverageVotePower,i.votePower),this.maxAveragePopularity=Math.max(this.maxAveragePopularity,i.popularity);let o=this.FilterMovieTitle(i.title);Utility.CharIsNumber(o.substring(0,1).toUpperCase())?e.push("#"):e.push(o.substring(0,1).toUpperCase())}this.GenerateLetterNav(e),this.pageCount=Math.ceil(t.length/Settings.itemsPerPage),this.currentPage=0,this.txtPositionP.innerHTML=this.currentPage+1+" of "+this.pageCount,this.txtPositionP2.innerHTML=this.currentPage+1+" of "+this.pageCount,this.LoadItems()},this.GenerateLetterNav=function(t){let e=["#","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],s=document.querySelector("#LetterNav");s.innerHTML="";for(let i=0;i<e.length;i++){let o=document.createElement("div");t.includes(e[i])?(o.classList.add("Active"),o.setAttribute("data-letter",e[i]),o.onclick=this.OnClickBtnLetter.bind(this)):o.classList.add("Inactive"),o.innerHTML=e[i]+"&nbsp;",s.appendChild(o)}},this.LoadItems=function(){this.items.innerHTML="";let t=null;t=this.bGetSuggested?this.lastData.suggested:this.lastData.watched;for(let e=this.currentPage*Settings.itemsPerPage;e<this.currentPage*Settings.itemsPerPage+Settings.itemsPerPage&&!(e>=t.length);e++){let s=null;s=this.bGetSuggested?new SuggestedMovie(t[e]):new WatchedMovie(t[e]),s.Init(),this.items.appendChild(s.domObject)}this.UpdatePositionText()},this.OnClickBtnFirst=function(){0!=this.currentPage&&(this.currentPage=0,this.LoadItems())},this.OnClickBtnPrevious=function(){this.currentPage>0&&(this.currentPage-=1,this.LoadItems())},this.OnClickBtnNext=function(){this.currentPage<this.pageCount-1&&(this.currentPage+=1,this.LoadItems())},this.OnClickBtnLast=function(){this.currentPage!=this.pageCount-1&&(this.currentPage=this.pageCount-1,this.LoadItems())},this.UpdatePositionText=function(){this.txtPositionP.innerHTML=this.currentPage+1+" of "+this.pageCount,this.txtPositionP2.innerHTML=this.currentPage+1+" of "+this.pageCount},this.OnClickBtnSetting=function(){let t=window.location.href;this.bGetSuggested?window.location.href=t.replace("suggested","watched"):window.location.href=t.replace("watched","suggested")},this.OnClickBtnVote=function(){window.location.href="/vote.html?server="+Utility.GetQueryValue("server")},this.OnClickBtnLetter=function(t){let e=t.target.getAttribute("data-letter"),s=null,i=[];i="#"==e?["0","1","2","3","4","5","6","7","8","9"]:[e],s=this.bGetSuggested?this.lastData.suggested:this.lastData.watched;let o=-1;for(let t=0;t<s.length;t++){for(let e=0;e<i.length;e++){let n=i[e],r=this.FilterMovieTitle(s[t].title),a=""!=r;if(a&=r.substring(0,1).toUpperCase()==n,a){o=t;break}}if(-1!=o)break}if(-1!=o){let t=Math.floor(o/Settings.itemsPerPage);this.currentPage=t,this.txtPositionP.innerHTML=this.currentPage+1+" of "+this.pageCount,this.txtPositionP2.innerHTML=this.currentPage+1+" of "+this.pageCount,this.LoadItems()}},this.matchTerms=["THE ","A "],this.FilterMovieTitle=function(t){let e=t;for(let s=0;s<this.matchTerms.length;s++){let i=this.matchTerms[s];t.substring(0,i.length).toUpperCase()==i&&(e=e.substring(i.length))}return e.length<1&&(e=t),e},this.UnselectAllBullets=function(){document.querySelector("#BtnSortByTitle .bullet").classList.remove("selected"),document.querySelector("#BtnSortBySuggestor .bullet").classList.remove("selected"),document.querySelector("#BtnSortBySuggestDate .bullet").classList.remove("selected"),document.querySelector("#BtnSortByWatchDate .bullet").classList.remove("selected"),document.querySelector("#BtnSortByVoteCount .bullet").classList.remove("selected")},this.SortyByTitle=function(){this.UnselectAllBullets(),document.querySelector("#BtnSortByTitle .bullet").classList.add("selected"),this.SortData(((t,e)=>{let s=MovieNightBot.FilterMovieTitle(t.title),i=MovieNightBot.FilterMovieTitle(e.title);return s.localeCompare(i)}))},this.SortBySuggestor=function(){this.UnselectAllBullets(),document.querySelector("#BtnSortBySuggestor .bullet").classList.add("selected"),this.SortData(((t,e)=>{let s=t.suggestor.localeCompare(e.suggestor);if(0==s){let i=MovieNightBot.FilterMovieTitle(t.title),o=MovieNightBot.FilterMovieTitle(e.title);s=i.localeCompare(o)}return s}))},this.SortBySuggestDate=function(){this.UnselectAllBullets(),document.querySelector("#BtnSortBySuggestDate .bullet").classList.add("selected"),this.SortData(((t,e)=>{let s=new Date(t.date_suggested),i=new Date(e.date_suggested);return s.getTime()>=i?-1:1}))},this.SortByWatchDate=function(){this.UnselectAllBullets(),document.querySelector("#BtnSortByWatchDate .bullet").classList.add("selected"),this.SortData(((t,e)=>{let s=new Date(t.date_watched),i=new Date(e.date_watched);return s.getTime()>=i?-1:1}))},this.SortByVoteCount=function(){this.UnselectAllBullets(),document.querySelector("#BtnSortByVoteCount .bullet").classList.add("selected"),this.SortData(((t,e)=>(val=0,t.total_votes>e.total_votes&&(val=-1),e.total_votes>t.total_votes&&(val=1),val)))},this.SortData=function(t){this.bGetSuggested?this.lastData.suggested=this.lastData.suggested.sort(t):this.lastData.watched=this.lastData.watched.sort(t),this.currentPage=0,this.LoadItems()}}function SettingsConstructor(){this.itemsPerPage=10}