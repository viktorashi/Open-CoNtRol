// Open and close sidebar
function w3_open() {
  document.getElementById("mySidebar").style.width = "100%";
  document.getElementById("mySidebar").style.display = "block";
}

function w3_close() {
  document.getElementById("mySidebar").style.display = "none";
}

// Generate Species List
function generateSpecs(specsList)
{
    undeVinSpeciile = document.getElementById("undeVinSpeciile"); undeVinSpeciile.innerHTML = "";
    specIndex = 0;
    for ( spec in specsList )
    {
        textToAppend = "<div class=\"form-group\">"+
                      "<div class=\"input-group\">"+
                      "<p style=\"display:inline;padding-right:10%\">"+specsList[specIndex]+"</p>"+
                      `<input placeholder="${specsList[specIndex]} concentration" required id="NumberButton" class="w3-input w3-hover-blue" style="width:60%; display:inline; text-align:center;margin-top:8%" type="number" step="any" name="valinit${specIndex}" >`+
                      "</div>"+
                      "</div>";
        specIndex++;
        undeVinSpeciile.innerHTML = undeVinSpeciile.innerHTML + textToAppend;
    }
}

// Generate Reaction Constants List
function generateConstante(constCount)
{
    let undeVinConstantele = document.getElementById("undeVinConstantele");
    undeVinConstantele.innerHTML = "";

    for ( let constIndex = 0; constIndex < constCount; constIndex++ )
    {
        textToAppend = "<div class=\"form-group\">"+
                "<div class=\"input-group\">"+
                "<p style=\"display:inline; padding-right:10%\">k"+(constIndex+1)+"</p>"+
                `<input placeholder="const ${constIndex+1} value" required id="NumberButton" class="w3-input w3-hover-blue" style="width:60%; display:inline;text-align:center; margin-top:8%" type="number" step="any" name="valk${constIndex}" >`+
                "</div>"+
                "</div>";

        undeVinConstantele.innerHTML = undeVinConstantele.innerHTML + textToAppend;
    }
}

function generateCheckBoxes(specsList){
    let checkBoxes = document.getElementById("checkBoxes");
    checkBoxes.innerHTML = "";

    for (let i = 0; i < specsList.length; i++){
        textToAppend = `<input type="checkbox" id="check${i}" name="check${i}" value="${specsList[i]}">`+
                       `<label for="check${i}">${specsList[i]}</label><br>`;

        checkBoxes.innerHTML = checkBoxes.innerHTML + textToAppend;
    }

}

function updateInputs(filename)
{
    const xhttp = new XMLHttpRequest();


    xhttp.onreadystatechange = () => {
        //when it's done/all data has been transmitted and status OK

        if (xhttp.status === 200) {
            console.log("e 200 codu ba")
        }

        if (xhttp.readyState === 4) {
            console.log("e gata requestuuuu")
        }

        if (xhttp.readyState === 4 && xhttp.status === 200) {
            let jsonOBJ;
            jsonOBJ = JSON.parse(xhttp.responseText);

            specsList = jsonOBJ.speciiList;
            reactsCount = jsonOBJ.reactsCount;
            specCount = specsList.length

            console.log(reactsCount)
            console.log(specsList)
            console.log(specCount)

            generateSpecs(specsList);
            generateConstante(reactsCount);
            generateCheckBoxes(specsList)
        }
    };

    xhttp.open("GET", "/crn_data?filename="+filename);
    xhttp.send();
}

function reactionFilenameChanged()
{
    selectorItem = document.getElementById('comp_select');

    updateInputs(selectorItem.value);
}

reactionFilenameChanged();

/*
Enable / Disable Button
*/
function doCheck(){
    let allFilled = true;

    let inputs = document.getElementsByTagName('input');
    for(let i=0; i < inputs.length; i++){
        if(inputs[i].value === '' && inputs[i].type === "number"){
            allFilled = false;
            break;
        }
    }

    document.getElementById("register").disabled = !allFilled;
}

window.onload = () =>{
    let inputs = document.getElementsByTagName('input');
    for(let i=0; i < inputs.length; i++){
        if(inputs[i].type === "number"){
            inputs[i].onkeydown = doCheck;
            inputs[i].onblur = doCheck;
        }
    }
};
