let countEcuatii = 1;

function updateFormReactCount(ecuatiiCount) {
    $("#ecuatiiCount").val(ecuatiiCount);
}

function genTextBox(textBoxID) {
    $("#textboxDiv").append(`<div>
	                            <br>
                                <input oninput="this.value = this.value.toUpperCase()" class="eq_box" name='ec_${textBoxID}_left' type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅' required/>
    							<select name='ec_${textBoxID}_dir' class='reaction_direction' >
         							<option value='left'>&#8592</option>
        							<option value='both' selected='selected'>⇌</option>
        							<option value='right'>&#8594</option>
    							</select>
    							<input oninput="this.value = this.value.toUpperCase()" class="eq_box" name='ec_${textBoxID}_right'  type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅' required/>
<!--    							delete button for the specific equations-->
<!--make it a delete with circle cross button-->
             					<button type='button' onclick='
             					 if (countEcuatii > 1) { 
             					    $(this).parent().remove(); 
             					    countEcuatii--;
                                    updateFormReactCount(countEcuatii);
             					    } 
             					    '> <i class="material-icons">delete</i> </button
                            <br></div> `);
}

function validEquation(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/pzO5MF or https://www.debuggex.com (so you can see it visually)
    *  */
    const regex = /^\s*[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))*\s*$/gm;
    return regex.test(str);
}

//will be used by de dropDownsFormSubmitHandler when it calls the FormData constructor
function dropDownsFormDataHandler(event) {
    console.log('form data a dat fire')
    //data cleansing a bit before checking validity and submitting

    // or     const formData = e.originalEvent.formData; if this one doesn't work
    const formData = event.formData;

    // formdata gets modified by the formdata event
    for (let i = 1; i <= countEcuatii; i++) {
        formData.set(`ec_${i}_left`, formData.get(`ec_${i}_left`).trim())
        formData.set(`ec_${i}_right`, formData.get(`ec_${i}_right`).trim())
    }
}

function dropDownsFormSubmitHandler() {
    // construct a FormData object, which fires the formdata event

    const dropDownsForm = document.forms['dropDownsForm']
    const submitterButton = document.getElementById('submitDropdownsButton')

    // dropDownsFromDataHandler is called when calling this constructor
    const formData = new FormData(dropDownsForm, submitterButton);

    console.log('cum au ajuns dupa');
    for (let i = 1; i <= countEcuatii; i++) {
        const box_left = formData.get(`ec_${i}_left`)
        const box_right = formData.get(`ec_${i}_right`)

        console.log(box_left)
        console.log(box_right)

        if (!validEquation(box_left) || !validEquation(box_right)) {
            document.getElementById('dropDownsError').innerText = 'A chemical reaction not valid'
            console.log('NA DAT MATCHH')
            //it's not safe to submit the form
            return false;
        }
    }
    //it's safe to submit the form
    return true;
}

function validEquation(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/pzO5MF or https://www.debuggex.com (so you can see it visually)
    *   It checks, for example:
    *       A + B
    *       2H2 + O2
    *       2H2O
    *  */
    const regex = /^\s*[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))*\s*$/gm;
    return regex.test(str);
}

function validAntimonyCRNDefinition(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/hjRLci or https://www.debuggex.com (to visually see it)
    *
    *   It checks, for example:
    *       2H2 + O2 -> 2H2O;  k1*H2*H2*O2
    *       C + O2 -> CO2; k2*C*O2
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

// Add textbox and remove textbox
$(document).ready(() => {

    genTextBox(countEcuatii);
    updateFormReactCount(countEcuatii);

    $("#Add").on("click", () => {
        countEcuatii++;
        genTextBox(countEcuatii);
        updateFormReactCount(countEcuatii);
    });
    $("#Remove").on("click", () => {
        if (countEcuatii > 1) {
            countEcuatii--;
            updateFormReactCount(countEcuatii);
            $("#textboxDiv").children().last().remove();
        }
    });
    $("#reset_reaction_button").on("click", () => {
        countEcuatii = 1;
        $("#textboxDiv").children().slice(0).remove();
        genTextBox(countEcuatii);
        updateFormReactCount(countEcuatii);
    });
});

function toggleForm() {
    const form = document.getElementById('crnForm');
    form.classList.toggle('open');
}
