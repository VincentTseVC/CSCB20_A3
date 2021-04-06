


function openTabContent(evt, tabContentId) {

    // hide all the tabcontents
    var tabcontents = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabcontents.length; i++) {
        // tabcontents[i].style.display = "none";
        tabcontents[i].className = tabcontents[i].className.replace(" active", "");
    }

    // remove the current actived tab
    var tablinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tablinks.length; i++)
    tablinks[i].className = tablinks[i].className.replace(" active", "");

    // expend the selected tabcontent
    document.getElementById(tabContentId).className += " active";
    evt.currentTarget.className += " active";
}