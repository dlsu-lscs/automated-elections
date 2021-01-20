function selectAllCollege(choice) {
    // Get all relevant inputs to be unchecked with the given name
    let inputs = document.getElementsByName(choice);

    // Then uncheck them all
    for (let index = 0; index < inputs.length; index++) {
        inputs[index].checked = true;
    }
}

function selectAll() {
    // Get all relevant inputs to be unchecked with the given name
    let inputs = document.querySelectorAll('input[type="checkbox"]');

    // Then uncheck them all
    for (let index = 0; index < inputs.length; index++) {
        inputs[index].checked = true;
    }
}

function setState(state) {
    let form = document.getElementById('election-form-type');

    switch (state) {
        case "start": form.value = 'start-elections'; break;
        case "pause": form.value = 'pause-elections'; break;
        case "resume": form.value = 'resume-elections'; break;
        case "end": form.value = 'end-elections'; break;
        case "unblock": form.value = 'unblock-results'; break;
        case "archive": form.value = 'archive-results'; break;
        default: form.value = 'start-elections';
    }

    showControls();
}