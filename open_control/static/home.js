let countEcuatii = 1;

function updateFormReactCount(ecuatiiCount)
{
	$("#ecuatiiCount").val(ecuatiiCount);
}

function genTextBox(textBoxID)
{
	$("#textboxDiv").append(`<div>
	                            <br>
                                <input name='ec_${textBoxID}_left' type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅'/>
    							<select name='ec_${textBoxID}_dir' class='reaction_direction' >
         							<option value='left'>&#8592</option>
        							<option value='both' selected='selected'>⇌</option>
        							<option value='right'>&#8594</option>
    							</select>
    							<input name='ec_${textBoxID}_right'  type='text' size='20' maxlength='64' value='' spellcheck='false' placeholder='∅'/>
                            <br></div> `);
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