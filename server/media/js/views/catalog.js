function checkForm(form) {
    var errorList = [];    
    for (var i = 0; i < form.elements.length; i++) {
    el = form.elements[i];
    elName = el.nodeName.toLowerCase();
    value = el.value;
    if (elName == "input") {
        type = el.type.toLowerCase();
        if( type == "text" && value == "") {
                errorList.push(1);
        }
    }
    }
if (!errorList.length) return true;
return false;

}

function checkExtForm(form) {
    var errorList = [];    
    for (var i = 0; i < form.elements.length; i++) {
    el = form.elements[i];
    elName = el.nodeName.toLowerCase();
    value = el.value;
    if (elName == "input") {
        type = el.type.toLowerCase();
        if( type == "text" && value == "") {
                errorList.push(1);
        }
    }
    if (elName == "select") {
        if( value == "") {
                errorList.push(1);
        }
    }

    }
if (errorList.length < 4) return true;
return false;

}
