function adduserMsg() {
    var text = document.getElementById("chat-text").value;
    if (text) {
        var ul = document.getElementById("chat-list");
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(text));
        li.setAttribute('class', 'list-group-item list-group-item-info user')
        ul.appendChild(li);
    }
}