window.onload = function(){
    load_camlist();
}

function findclass(serialno) {
    var cameraclass = "None";
    var table = document.getElementById("camlist");
    for (var i = 1; i < table.rows.length; i++){
        if (table.rows[i].cells[1].innerHTML == serialno){
            cameraclass = table.rows[i].cells[3].innerHTML;
        }
    }
    return cameraclass
}

function Enter() {
    if (document.getElementById("bottomcam").innerHTML == "None" && document.getElementById("sidecam").innerHTML != "None"){
        document.getElementById("error").innerHTML = "Bottom Camera is not selected.";
        return -1
    }

    var list = [0, [-1, "None"], [-1, "None"]];  //num, bottom[id, class], side[id, class]
    var arr = ["bottomcam", "sidecam"]

    arr.forEach((elem, index) => {
        id = document.getElementById(elem).innerHTML;
        if (id != "None"){
            list[index + 1] = [id, findclass(id)];
            list[0]++;
        }
    })

    eel.get_num(list);
    open('about:blank', '_self').close();
}

function load_camlist() {
    document.getElementById('Enter').disabled = true;
    document.getElementById('Load').disabled = true;
    document.getElementById("error").innerHTML = "";
    eel.py_camlist();
}

function select_camera() {
    document.getElementById("error").innerHTML = "";
    document.getElementById("bottomcam").innerHTML = "None";
    document.getElementById("sidecam").innerHTML = "None";

    var table = document.getElementById("camlist");
    var bn = [0, ""], sn = [0, ""]; // number, name

    for (var i = 0; i < table.rows.length - 1; i++){
        var st = document.getElementById("select_tab" + i);
        if (st.value == "bottom"){
            bn[0] ++;
            bn[1] = table.rows[i+1].cells[1].innerHTML;
        }
        else if (st.value == "side"){
            sn[0] ++;
            sn[1] = table.rows[i+1].cells[1].innerHTML;
        }
    }

    if (bn[0] == 1){
        document.getElementById("bottomcam").innerHTML = bn[1];
    }
    else if (bn[0] > 1){
        document.getElementById("error").innerHTML = "Error";
    }

    if (sn[0] == 1){
        document.getElementById("sidecam").innerHTML = sn[1];
    }
    else if (sn[0] > 1){
        document.getElementById("error").innerHTML = "Error";
    }

    if (bn[0] == 0 && sn[0] == 0){
        document.getElementById("error").innerHTML = "Non cam mode";
    }
}

eel.expose(js_camlist)
function js_camlist(list_info) {
    var table = document.getElementById("camlist");
    var row_num = table.rows.length;

    var result = false;

    for (let key in list_info){
        if (list_info[key] != 0){
            result = true;
            break;
        }
    }

    if (result == false) {
        document.getElementById("error").innerHTML = "No any cameras !";
        document.getElementById("bottomcam").innerHTML = "None";
        document.getElementById("sidecam").innerHTML = "None";
        return ;
    }

    if (row_num > 1) {
        while (row_num > 1) {
            table.deleteRow(row_num - 1);
            row_num = table.rows.length;
        }
    }
    var count = 0
    for (let key in list_info){
        for (var j = 0; j < list_info[key].length; j++){
            var newtr = table.insertRow(count + 1);
            cells_num = table.rows[0].cells.length;
            for (var i = 0; i < cells_num; i++){
                var newtd = newtr.insertCell(newtr.cells.length);
    
                if (i == 0) {
                    newtd.appendChild(document.createTextNode(count));
                }
                else if (i == 3){
                    newtd.appendChild(document.createTextNode(key));
                }
                else if (i == 4) {
                    var select_tab = document.createElement("select");
                    select_tab.id = "select_tab" + count;
                    select_tab.style.fontSize = "12pt";
                    select_tab.style.fontFamily = "Times New Roman";
                    select_tab.onchange = select_camera;
    
                    if (Object.keys(list_info).length == 1) {
                        select_tab.innerHTML = '<option value="select">select</option>'
                            + '<option value="bottom">bottom</option>';
                    }
                    else {
                        select_tab.innerHTML = '<option value="select">select</option>'
                            + '<option value="bottom">bottom</option>'
                            + '<option value="side">side</option>';
                    }
                    newtd.appendChild(select_tab);
                }
                else {
                    newtd.appendChild(document.createTextNode(list_info[key][j][i - 1]));
                }
            }
            count++;
        }
    }
    document.getElementById('Enter').disabled = false;
    document.getElementById('Load').disabled = false;

}