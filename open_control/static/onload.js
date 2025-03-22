// assigns the validation function to the input fields
export function onloadFunc(validationFunc) {
    let inputs = document.getElementsByTagName('input');
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === "number") {
            inputs[i].onkeydown = validationFunc;
            inputs[i].onblur = validationFunc;
        } else if (inputs[i].type === 'checkbox') {
            inputs[i].onchange = validationFunc;
        }

    }
};
