window.dimmerSwitch = true;

function gohome() {
	window.location.assign("/");
}
function navigate(page) {
	//window.location.assign("/" + chapter + "/" + page);
	window.location.assign("/" + page);
}
function navMenu() {
	var fb = document.getElementsByClassName("fancy-nav-box")[0];
	if (fb.style.bottom == "-74px") {
		fb.style.bottom="37px";
	} else {
		fb.style.bottom="-74px";
	}
}
function changeChapter(page, chapter, move) {
	if (move == 'next') {
		window.location.assign("/" + (page + 1) + "/" + (chapter + 1));
	} else {
		window.location.assign("/" + (page - 1) + "/" + (chapter - 1));
	}
}

function fontScale(n) {
	var t = document.getElementById("content-text");
	t.style.fontSize = n + "px";
}

function quotePretty() {
	//dimmer cookie
	var dimmerCookie = document.cookie;
	dimmerCookie = dimmerCookie.split(';');
	dimmerCookie = dimmerCookie[0];
	
	if (dimmerCookie.includes("false")) {
		dimmerSwitch = false;
		//dimmer();
	}

	var t = document.getElementById("content-text");
	var txt = t.innerHTML;
	var first = true;
	for (const c of txt) {
		if (c == "\"") {
			if (first) {
				txt.replace(c, "<span class=quote>\"");
			} else {
				txt.replace(c, "\"</span>");
			}
			first = !first;
		}
	}
	t.innerHTML = txt;
	return true;
}

function dimmer() {
	var i = document.getElementById("lightSwitch");
	var b = document.getElementsByTagName("BODY")[0];
	var cm = document.getElementsByClassName("content-main")[0];
	var ct = document.getElementsByClassName("content-text")[0];
	var t = document.getElementsByClassName("title-sub")[0];
	var tm = document.getElementsByClassName("title-main")[0];
	var tt = document.getElementsByClassName("title-top")[0];
	var anchors = document.getElementsByClassName("char-anchor");
	var acolour = "#660025";

	if (dimmerSwitch) {
		i.src = "/static/images/lightOff.png";
		b.style.backgroundColor = "#222";
		cm.style.backgroundColor = "#333";
		cm.style.backgroundImage="none";
		ct.style.color = "#999";
		acolour = "#8b7896";
		tt.style.color = acolour;
	       try {
			tm.style.color = "#999";
			t.style.color = "#999";
		} catch (err) { }

	} else {
		i.src = "/static/images/light.png";
		b.style.backgroundColor = "#984029";
		//cm.style.backgroundColor = "#EFEFE3";
		cm.style.backgroundImage="url('/static/images/lightPaper.jpg')";
		ct.style.color = "#000";
		acolour = "#660025";
		tt.style.color = "#feffd4";
		try {
			tm.style.color = "#333";
			t.style.color = "#333";
		} catch (err) {}
	}

	for (var i=0; i<anchors.length;i++) {
		anchors[i].style.color = acolour;
	}

	dimmerSwitch = !dimmerSwitch;
	document.cookie = "dimmerCookie=" + dimmerSwitch + ";path=/;";
}

function show(s) {
	var contents = document.getElementById("Contents-div");
	var chars = document.getElementById("Characters-div");
	var places = document.getElementById("Places-div");

	var c = document.getElementById("show-info");
	var h = c.offsetHeight;

	if (c.style.bottom != "38px") {
		c.style.bottom = "38px";
	} else {
		//c.style.bottom = (0-h) + "px";
	}

	switch(s) {
		case "Contents":
			chars.style.display = "none";
			places.style.display = "none";
			contents.style.display = "block";
			break;
		case "Characters":
			places.style.display = "none";
			contents.style.display = "none";
			chars.style.display = "block";
			break;
		case "Places":
			chars.style.display = "none";
			contents.style.display = "none";
		       	places.style.display = "block";
			break;
		default:
			c.style.bottom = (0-h) + "px";
			break;
	}
}
function start() {
	quotePretty();
}
function showHint(e, name) {
	var hint = document.getElementById("hint");
	var rect = document.getElementsByTagName("BODY")[0].getBoundingClientRect();
	
	var l = (e.clientX - rect.left) + "px";
	var t = (e.clientY - rect.top) + "px";

	hint.style.left = l;
	hint.style.top = t;

	var hints = {
		"Rinn":"Rinn, captain of the squad, something something",
		"Smim":"The spoiled rich wimp who needs to toughen up",
		"Brob":"The boisterous moustachioed strongman, destroyer of ... anything!",
		"Rack":"The beautiful adonis scoundrel and ladies man extraordinaire",
		"Arissa":"The girly rich girl with serious outdoor experience",
		"Sephra":"The streetwise home-brewer with a streak of berserker rage",
		"Trufty":"The young knight-to-be with a lot to prove and some glorious hair"

	}

	hint.innerHTML = hints[name];
	
	if (hint.style.display == "none" || hint.style.display == "") {
		hint.style.display = "block";
	} else {
		hint.style.display = "none";
	}

	return false;
}
function hideHint() {
	var hint = document.getElementById("hint");
	hint.style.display = "none";
}
function buy(b) {
	window.location.assign("/buy/" + b);
}
