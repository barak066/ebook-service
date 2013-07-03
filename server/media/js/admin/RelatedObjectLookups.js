function checkboxDismissRelatedLookupPopup(win, chosenId, chosenName) {
    var name = windowname_to_id(win.name) + "_0";
    var elem = document.getElementById(name);
    if (elem == null) {
        var elem = document.getElementById("lookup_id_author");
        var ul = elem.parentNode;
    }
    else {    
        ul = elem.parentNode.parentNode.parentNode;
    }
    var li = document.createElement('li'); 

    var chkbox = document.createElement('input');    
    chkbox.type = "checkbox";
    chkbox.id = 'id_author' + chosenId;
    chkbox.name = 'author';
    chkbox.checked="checked";
    chkbox.value=chosenId;

    var label = document.createElement('label');    
    label.htmlFor = 'id_author' + chosenId;
    label.appendChild(chkbox);
    label.appendChild( document.createTextNode(chosenName));
    li.appendChild(label);        
    ul.appendChild(li);    

    win.close();
}

function showAnnotationPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);

    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1';
    } else {
        href = triggeringLink.href + '?pop=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function annotationDismissRelatedLookupPopup(win, chosenId, chosenName) {

    var elem = document.getElementById("id_annotation_"+chosenId);
  
    label = elem.parentNode;
    label.innerHTML = '<input checked="checked" name="annotation" value="' + chosenId +'" id="id_annotation_'+ chosenId + '" type="checkbox" class="vManyToManyRawIdAdminField" /><a href="../../annotation/' + chosenId + '/" onclick="return showRelatedObjectLookupPopup(this);">'+ chosenName + '</a>';

    win.close();
}
