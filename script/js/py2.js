eel.expose(py2js);
eel.expose(GUINodeChange);
eel.expose(PrintLog);
eel.expose(jsChangeValue);
eel.expose(jsChangeText);
eel.expose(CreateObj);
eel.expose(DeleteObj);
eel.expose(BR);
eel.expose(HideObj);
eel.expose(ShowObj);

function py2js(id){
    var obj = document.getElementById(id);
    return obj.value
}

function GUINodeChange(id, val, state, category){
    var elem = document.getElementById(id + category);
    if (category == 'trackbar'){
        if (state == 'max'){
            elem.max = val;
        }
        else if (state == 'min'){
            elem.min = val;
        }
        else if (state == 'now'){
            elem.value = val;
        }
    }
    else if (category == 'textbox'){
        if (state == 'now'){
            elem.value = val;
        }
    }
}

function PrintLog(string){
    var obj = document.getElementById('main_textarea');
    obj.innerHTML += (string + "\n");
    obj.scrollTop = obj.scrollHeight;
}

function jsChangeValue(id, val){
    var obj = document.getElementById(id);
    obj.value = val;
}

function jsChangeText(id, val){
    var obj = document.getElementById(id);
    obj.textContent = val;
}

function CreateObj(parentid, id, tagName, val){
    var parentobj = document.getElementById(parentid);
    if(parentobj == null){
        return -1;
    }

    var obj = document.getElementById(id);
    if(obj == null){
        if(!isNaN(val)){
            val = Number(val);
        }

        obj = document.createElement(tagName);
        obj.id = id;
        obj.value = val;
        obj.textContent = val;
        obj.onchange = function f(){js2py(this.value, this.id)};
        
        parentobj.insertBefore(obj, null);
    }
}

function DeleteObj(id){
    var obj = document.getElementById(id);
    if(obj != null){
        obj.remove();
    }
}

function BR(parentid){
    var parentobj = document.getElementById(parentid);
    if(parentobj == null){
        return -1;
    }
    parentobj.insertBefore(document.createElement("br"), null);
}

function HideObj(id){
    var obj = document.getElementById(id);
    if(obj != null){
        obj.style.display = "none";
    }
}

function ShowObj(id){
    var obj = document.getElementById(id);
    if(obj != null){
        obj.style.display = "";
    }
}
