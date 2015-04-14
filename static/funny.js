function isFilled(field) {
    if (field.value.replace(' ', '').length === 0)
    {
        return false;
    }
    var placeholder = field.placeholder || field.getAttribute('placeholder');
    return field.value != placeholder;
}

function isEmail (field) {
    var indexOfat = field.value.indexOf('@');
    var indexOfdot = field.value.indexOf('.');
    return indexOfat !== -1 && indexOfdot !== -1;
}

function gethttpobject() {
    if (typeof XMLHttpRequest == "undefined") 
        XMLHttpRequest = function() {
            try {return new ActiveXObject("Msxml2.XMLHTTP.6.0"); }
            catch (e) {}
            try {return new ActiveXObject("Msxml2.XMLHTTP.3.0"); }
            catch (e) {}
            try {return new ActiveXObject("Msxml2.XMLHTTP"); }
            catch (e) {}
            return false;
        };

    return new XMLHttpRequest();
}

window.onload = function() {
    // TODO
};
