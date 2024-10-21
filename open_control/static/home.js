let countEcuatii = 1;

function updateFormReactCount(ecuatiiCount)
{
	$("#ecuatiiCount").val(ecuatiiCount);
}

function genTextBox(textBoxID)
{
	$("#textboxDiv").append(`<div>
	                            <br>
                                <input class="eq_box" name='ec_${textBoxID}_left' type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅' required/>
    							<select name='ec_${textBoxID}_dir' class='reaction_direction' >
         							<option value='left'>&#8592</option>
        							<option value='both' selected='selected'>⇌</option>
        							<option value='right'>&#8594</option>
    							</select>
    							<input class="eq_box" name='ec_${textBoxID}_right'  type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅' required/>
                            <br></div> `);
}

function validateForm(){
	  for(let i = 1; i <= countEcuatii; i++ ){
		  const box_left = document.forms['form'][`ec_${i}_left`].value
		  const box_right = document.forms['form'][`ec_${i}_right`].value
		  if (!(validEquation(box_left) || validEquation(box_right))){
			  document.getElementsByClassName('errors')[0].innerText = 'Not a valid chemical equationn!!'
			  console.log('NA DAT MATCHH')
			  return false;
		  }
	  }
	  return true;
}
function validEquation(str) {
	const regex = /^[0-9]*([a-zA-Z]{1,2}[0-9]*)+( \+ [0-9]*([a-zA-Z]{1,2}[0-9]*))*$/gm;
    return regex.test(str);
}

// Add textbox and remove textbox
$(document).ready(() => {
			genTextBox(countEcuatii);
			updateFormReactCount(countEcuatii);

            $("#Add").on("click",() => {
				countEcuatii++;
				genTextBox(countEcuatii);
				updateFormReactCount(countEcuatii);
			} );
            $("#Remove").on("click", () => {
				if (countEcuatii > 1)
				{
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

function saveToDB()
{
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