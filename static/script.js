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

    addbotMsgRTL("Starting Registration");
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
        if (res["status"] == "successfully registered") {
            addbotMsgRTL("Successfully registered");
            const element = document.getElementById("rForm");
            element.remove();
        } else {
            addbotMsgRTL(res["status"]);
        }
    } catch (err) {
        console.error(`ERROR: ${err}`);
    }
}

async function noReg() {
    const element = document.getElementById("rForm");
    element.remove();
    addbotMsgRTL('Cancelled Registration');
    login(true);
}

function login(isChained = false) {
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
    var email = document.getElementById("InputEmail2").value;
    var pword = document.getElementById("InputPassword2").value;

    try {
        const req = await fetch(url + "api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },

            // format the data
            body: JSON.stringify({
                email: email,
                password: pword
            }),
        });

        const res = await req.json();

        // Log success message
        console.log(res);
        if (res["status"] == "done" && res['token'] != null) {
            addbotMsgRTL("Done");
            const element = document.getElementById("lForm");
            element.remove();
            // cookies setup
            Cookies.set("token", res['token'], { expires: 7 });
            tokenID = Cookies.get('token');
        } else {
            addbotMsgRTL(res["status"]);
        }
    } catch (err) {
        console.error(`ERROR: ${err}`);
    }
}

async function loginCancel() {
    const element = document.getElementById("lForm");
    element.remove();
    addbotMsgRTL('Cancelled Login');
}

function OOD_form() {
    var formDiv = document.createElement("div");
    var myRequest = new Request(url + "OODL.html");
    fetch(myRequest).then(async function (response) {
        const text = await response.text();
        formDiv.innerHTML = text;
    });
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(formDiv);
    li.setAttribute("class", "bot");
    li.setAttribute("id", "OODLForm");
    ul.appendChild(li);
    li.scrollIntoView({ behavior: "smooth" });
}

// make this one work
async function OOD_form_handel() {
    var reason = document.getElementById("reason").value;
    var start = document.getElementById("start").value;
    var end = document.getElementById("end").value;
    var cause = document.getElementById("cause").value;
    var hours = document.getElementById("Hours").value;
    try {
        // Create request to api service
        const req = await fetch(url + "api/OODL", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },

            // format the data
            body: JSON.stringify({
                reason: reason,
                start: start,
                end: end,
                token: tokenID,
                cause: cause,
                hours: hours
            }),
        });

        const res = await req.json();

        // Log success message
        console.log(res);
        addbotMsgRTL(res["status"]);
        const element = document.getElementById("OODLForm");
        element.remove();
    } catch (err) {
        console.error(`ERROR: ${err}`);
    }
}

async function OOD_form_Cancel() {
    const element = document.getElementById("OODLForm");
    element.remove();
    addbotMsgRTL('Removing Form');
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
            if (res["class"][0]["intent"] == "OOD_form" || res["class"][0]["intent"] == "leave_form") {
                OOD_form();
            }
            if (res["class"][0]["intent"] == "time_now") {
                const reqw = await fetch(url + "api/timedelta", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },

                    // format the data
                    body: JSON.stringify({
                        delta: '0'
                    }),
                });
                const ress = await reqw.json();
                console.log(res, ress);
                addbotMsgRTL(ress["results"]);
            }
            if (res["class"][0]["intent"] == "time_deltas") {
                const reqw = await fetch(url + "api/timedelta", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },

                    // format the data
                    body: JSON.stringify({
                        delta: text
                    }),
                });
                const ress = await reqw.json();
                console.log(res, ress);
                addbotMsgRTL(ress["results"]);
            }
            if (res["class"][0]["intent"] == "show_attendance") {
                addbotMsgRTL(res["results"]);
                const reqw = await fetch(url + "api/graph", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },

                    // format the data
                    body: JSON.stringify({
                        token: tokenID
                    }),
                });
                const ress = await reqw.json();
                console.log(ress['attendance']);
                addbotMsgRTL(ress["attendance"]);
            }
            else {
                console.log('here')
                if (res["results"] != "DNP")
                    addbotMsgRTL(res["results"]);
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

// RTL for RealTimeL???
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
