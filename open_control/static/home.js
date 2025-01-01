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

function validAntimonyCRNDefinition(str) {
    /*
    *	when in doubt, debug it in : https://regex101.com/library/hjRLci or https://www.debuggex.com (to visually see it)
    *  */
    const regex = /^[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))* *-> *[0-9]* *([a-zA-Z]+[0-9]*)+( *\+ *[0-9]*([a-zA-Z]{1,2}[0-9]*))* *; *[a-z][0-9]+( *\* *[0-9]*([a-zA-Z]{1,2}[0-9]*))*$/gm
    return regex.test(str)
}

function validEquationsFormat(str) {

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

});

let timeoutId;

$('form input, form select').on('input propertychange change', () => {
    console.log('Textarea Change');

    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
        // Runs 1 second (1000 ms) after the last change    
        saveToDB();
    }, 1000);
});

function saveToDB() {
    console.log('Saving to the db');
    //form = genauto(),
    // form = $('.textboxDiv');
    form = $('.textbox');
    //  form = $('.textbox').each(() => {
    //          form += $(this).val() + "\n";
    //      });
    $.ajax({
        url: "/echo/html/",
        type: "POST",
        data: form.serialize(), // serializes the form's elements.
        beforeSend: (xhr) => {
            // Let them know we are saving
            $('.form-status-holder').html('Saving...');
        },
        success: (data) => {
            let jqObj = jQuery(data); // You can get data returned from your ajax call here. ex. jqObj.find('.returned-data').html()
            // Now show them we saved and when we did
            let d = new Date();
            $('.form-status-holder').html('Saved! Last: ' + d.toLocaleTimeString());
        },
    });
}


// This is just so we don't go anywhere
// and still save if you submit the form
// $('.contact-form').submit((e) => {
//	saveToDB();
//	e.preventDefault();
// });


// Toggle grid padding
function myFunction() {
    let x = document.getElementById("myGrid");
    if (x.className === "w3-row") {
        x.className = "w3-row-padding";
    } else {
        x.className = x.className.replace("w3-row-padding", "w3-row");
    }
}

// Open and close sidebar
function w3_open() {
    document.getElementById("mySidebar").style.width = "100%";
    document.getElementById("mySidebar").style.display = "block";
}

function w3_close() {
    document.getElementById("mySidebar").style.display = "none";
}