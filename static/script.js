const url = 'http://127.0.0.1:5000/'

async function adduserMsg() {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(text));
        li.setAttribute('class', 'list-group-item list-group-item-info user')
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
        document.getElementById("chat-text").value=''
    }
}


async function addbotMsg(msg) {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(msg));
        li.setAttribute('class', 'list-group-item list-group-item-success bot')
        ul.appendChild(li);
    }
}