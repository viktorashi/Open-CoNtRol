/*
Enable / Disable Button
*/
function checkValid() {
    let allFilled = true;
    let atLeastACheckbox = false;

    let inputs = document.getElementsByTagName('input');
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].value === '' && inputs[i].type === "number") {
            allFilled = false;
            break;
        } else if (!atLeastACheckbox && inputs[i].type === "checkbox" && inputs[i].checked) {
            atLeastACheckbox = true;
        }
    }

    document.getElementById("register").disabled = !(allFilled && atLeastACheckbox);
}

window.onload = () => {
    let inputs = document.getElementsByTagName('input');
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === "number") {
            inputs[i].onkeydown = checkValid;
            inputs[i].onblur = checkValid;
        } else if (inputs[i].type === 'checkbox') {
            inputs[i].onchange = checkValid;
        }

    }
};
