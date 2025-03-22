import {onloadFunc} from './onload.js'

// Open and close sidebar
function w3_open() {
    document.getElementById("mySidebar").style.width = "100%";
    document.getElementById("mySidebar").style.display = "block";
}

function w3_close() {
    document.getElementById("mySidebar").style.display = "none";
}

/*
Enable / Disable Button
*/
function checkValid() {
    let inputs = document.getElementsByTagName('input');

    let empty = false;
    let checkedBoxes = 0;
    for (let i = 0; i < inputs.length; i++) {
        //first checks the number inputs
        if (inputs[i].type === "number" && inputs[i].value === '') {
            empty = true;
        }
        //then checks the checkboxes
        else if (inputs[i].type === "checkbox" && inputs[i].checked) {
            checkedBoxes++;
        }
    }

    const checkedWell = 2 <= checkedBoxes && checkedBoxes <= 3;

    // disables if either one is bad
    document.getElementById("register").disabled = empty || !checkedWell;
}

window.onload = () => {
    onloadFunc(checkValid)
}