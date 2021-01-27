function openMessage() {
    document.getElementById('required-polls').style.display = "block";
}

function closeMessage() {
    document.getElementById('required-polls').style.display = "none";
}

window.onclick = function (event) {
    if (event.target === document.getElementById('required-polls')) {
        closeMessage();
    }
};