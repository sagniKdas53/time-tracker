const url = "http://127.0.0.1:5000/";
var tokenID = ""
function keyEvent(event) {
    event.preventDefault();
    if (event.key == "Enter") {
        adduserMsg();
    }
}

function first_visit() {
    addbotMsgRTL(
        "Hi! I am Kronii bot. I help you to keep your time-sheets in order"
    );
    addbotMsgRTL(
        'Send a message as "register" to start registration or "login" to login'
    );
    register();
}

async function register() {
    // make it so that the next message can be used to register directly
    var formDiv = document.createElement("div");
    var myRequest = new Request(url + "rform.html");
    fetch(myRequest).then(async function (response) {
        const text = await response.text();
        formDiv.innerHTML = text;
    });
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(formDiv);
    li.setAttribute("class", "bot");
    li.setAttribute("id", "rForm");
    ul.appendChild(li);
    li.scrollIntoView({ behavior: "smooth" });
}

async function regcmp() {
    //console.log('here');
    var name = document.getElementById("InputName").value;
    var email = document.getElementById("InputEmail1").value;
    var pword = document.getElementById("InputPassword1").value;
    console.log(name, email, pword);

    addbotMsgRTL("Resgistering");
    try {
        // Create request to api service
        const req = await fetch(url + "api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },

            // format the data
            body: JSON.stringify({
                name: name,
                email: email,
                password: pword,
                action: "register",
            }),
        });

        const res = await req.json();

        // Log success message
        //console.log(res);
        if (res["status"] == "done") {
            addbotMsgRTL("Done");
            const element = document.getElementById("rForm");
            element.remove();
        } else {
            addbotMsgRTL(res["status"]);
        }
    } catch (err) {
        console.error(`ERROR: ${err}`);
    }
}

function login(isChained = false) {
    // make it so that the next message can be used to register directly
    //console.log(isChained);
    if (isChained) {
        const element = document.getElementById("rForm");
        element.remove();
    }
    var formDiv = document.createElement("div");
    var myRequest = new Request(url + "lform.html");
    fetch(myRequest).then(async function (response) {
        const text = await response.text();
        formDiv.innerHTML = text;
    });
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(formDiv);
    li.setAttribute("class", "bot");
    li.setAttribute("id", "lForm");
    ul.appendChild(li);
    li.scrollIntoView({ behavior: "smooth" });
}

async function loginHandel() {
    var email = document.getElementById("InputEmail1").value;
    var pword = document.getElementById("InputPassword1").value;
    //console.log(email, pword);

    //addbotMsgRTL("Logging you in");
    try {
        // Create request to api service
        const req = await fetch(url + "api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },

            // format the data
            body: JSON.stringify({
                email: email,
                password: pword,
                action: "login",
            }),
        });

        const res = await req.json();

        // Log success message
        console.log(res);
        if (res["status"] == "done" && res['token'] != null) {
            addbotMsgRTL("Done");
            const element = document.getElementById("lForm");
            element.remove();
            // cookies set
            Cookies.set("token", res['token'], { expires: 7 });
            tokenID = Cookies.get('token');
        } else {
            addbotMsgRTL(res["status"]);
        }
    } catch (err) {
        console.error(`ERROR: ${err}`);
    }
}


async function logOutHandel() {
    if (Cookies.get('token')) {
        tokenID = '';
        Cookies.remove('token');
        addbotMsgRTL('Logged Out');
    } else {
        addbotMsgRTL('You are not signed in');
    }
}

function other_visit() {
    var msgSpan = document.createElement("div");
    msgSpan.innerHTML = "Hi! Welcome back!";
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(msgSpan);
    li.setAttribute("class", "bot");
    ul.appendChild(li);
    li.scrollIntoView({ behavior: "smooth" });
}

async function adduserMsg() {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var msgSpan = document.createElement("div");
        msgSpan.innerHTML = text;
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(msgSpan);
        li.setAttribute("class", "user");
        ul.appendChild(li);
        li.scrollIntoView({ behavior: "smooth" });

        try {
            // Create request to api service

            const req = await fetch(url + "api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },

                // format the data
                body: JSON.stringify({
                    body: text,
                    token: tokenID
                }),
            });

            const res = await req.json();

            // Log success message
            console.log(text, '\n', res);
            if (res["class"][0]["intent"] == "register") {
                register();
            }
            if (res["class"][0]["intent"] == "login") {
                login();
            }
            if (res["class"][0]["intent"] == "logout") {
                logOutHandel();
            }
            else {
                addbotMsg(res["results"]);
            }
        } catch (err) {
            console.error(`ERROR: ${err}`);
        }
    }
    document.getElementById("chat-text").value = "";
}

async function addbotMsg(msg) {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var msgSpan = document.createElement("div");
        msgSpan.innerHTML = msg;
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(msgSpan);
        li.setAttribute("class", "bot");
        ul.appendChild(li);
        li.scrollIntoView({ behavior: "smooth" });
    }
}

function addbotMsgRTL(msg) {
    var msgSpan = document.createElement("div");
    msgSpan.innerHTML = msg;
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(msgSpan);
    li.setAttribute("class", "bot");
    ul.appendChild(li);
    li.scrollIntoView({ behavior: "smooth" });
}

function cooker() {
    if (Cookies.get('token')) {
        tokenID = Cookies.get('token');
        other_visit();
    } else {
        first_visit();
    }
}
