const url = 'http://127.0.0.1:5000/'

function first_visit() {
    var msgSpan = document.createElement('div')
    msgSpan.innerHTML = 'Hi! I am Koroni bot';
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(msgSpan);
    li.setAttribute('class', 'bot')
    ul.appendChild(li);
    var msgSpan = document.createElement('div')
    msgSpan.innerHTML = 'I help you to keep your time-sheets in order';
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(msgSpan);
    li.setAttribute('class', 'bot')
    ul.appendChild(li);
}

function other_visit() {
    var msgSpan = document.createElement('div')
    msgSpan.innerHTML = 'Hi! Welcome back!';
    var ul = document.getElementById("chat-list");
    var li = document.createElement("li");
    li.appendChild(msgSpan);
    li.setAttribute('class', 'bot')
    ul.appendChild(li);
}

async function adduserMsg() {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var msgSpan = document.createElement('div')
        msgSpan.innerHTML = text;
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(msgSpan);
        li.setAttribute('class', 'user')
        ul.appendChild(li);

        try {
            // Create request to api service
            const req = await fetch(url + 'api/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },

                // format the data
                body: JSON.stringify({
                    body: text
                }),
            });

            const res = await req.json();

            // Log success message
            console.log(res);
            addbotMsg(res['results']);
        } catch (err) {
            console.error(`ERROR: ${err}`);
        }
        document.getElementById("chat-text").value = ''
    }
}


async function addbotMsg(msg) {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(msg));
        li.setAttribute('class', 'bot')
        ul.appendChild(li);
    }
}

function cooker() {
    console.log('here-co')
    if (!Cookies.get('first_visit')) {
        Cookies.set('first_visit', 'False', { expires: 7 });
        first_visit();
    } else {
        other_visit();
    }
}