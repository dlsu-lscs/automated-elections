function showControls() {
    // Show the summary modal
    document.getElementById('election-modal').style.display = "block";
}

function closeModal() {
    document.getElementById('election-modal').style.display = "none";
}

window.onclick = function (event) {
    if (event.target === document.getElementById('election-modal')) {
        closeModal();
    }
};