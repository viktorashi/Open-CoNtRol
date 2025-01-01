function validEquation(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/pzO5MF or https://www.debuggex.com (so you can see it visually)
    *  */
    const regex = /^\s*[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))*\s*$/gm;
    return regex.test(str);
}

function validAntimonyCRNDefinition(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/hjRLci or https://www.debuggex.com (to visually see it)
    *  */
    const regex = /^[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))* *-> *[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))* *; *[a-z][0-9]+( *\* *[0-9]*([a-zA-Z]{1,2}[0-9]*))*$/gm
    return regex.test(str)
}

function validEquationsFormat(str) {
    /**
     * combines validEquation and just looks to see if there's an arrow in there between them
     */
        // check if it has only one occurance of '->'
    const equations = str.split('\n')
    for (const equation of equations) {
        const theSplit = equation.split('->')
        if (theSplit.length !== 2) {
            return false;
        }
        const [leftSide, rightSide] = theSplit
        if (!validEquation(leftSide) || !validEquation(rightSide))
            return false;
    }
    return true;
}

//will be used by de antimonyFormSubmitHandler when it calls the FormData constructor
function antimonyFormDataHandler(event) {
    console.log('form data a dat fire');

    //data cleansing a bit before checking validity and submitting

    // or     const formData = e.originalEvent.formData; if this one doesn't work
    const formData = event.formData;

    formData.set('antimony-textarea', formData.get('antimony-textarea').trim());
    formData.set('antimony-textarea', formData.get('antimony-textarea').replace(/ +/gm, ' ')); //delete extra spacing
}

function antimonyFormSubmitHandler() {
    const antimony_code = document.forms['antimony_form']
    const submitterButton = document.getElementById('antimonySubmitButton')

    console.log('astea inainte sa dai formdata')
    console.log(antimony_code)
    const formData = new FormData(antimony_code, submitterButton);
    console.log('astea dupa sa dai formdata')
    console.log(formData.get('antimony-textarea'))

    const code = formData.get('antimony-textarea').split('\n\n')[0]

    if (validAntimonyCRNDefinition(code)) {
        $('#format').val('antimony')
        //it's safe to submit the form
        return true;
    }

    if (validEquationsFormat(code)) {
        $('#format').val('simple')
        //it's safe to submit the form
        return true;
    }
    document.getElementById('antimonyError').innerText = 'Neither antimony nor simple format valid'
    console.log('NA DAT MATCHH')
    //it's not safe to submit the form
    return false;
}

// Open and close sidebar
function w3_open() {
    document.getElementById("mySidebar").style.width = "100%";
    document.getElementById("mySidebar").style.display = "block";
}

function w3_close() {
    document.getElementById("mySidebar").style.display = "none";
}