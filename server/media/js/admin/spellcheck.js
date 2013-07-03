function addLoadEvent() {
    var elems = document.getElementsByTagName("textarea");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        // TODO path to media
        var googie1 = new GoogieSpell("/media/googiespell/", "/spellcheck/?lang="); 
        googie1.decorateTextarea(elem.id);
    }
}

