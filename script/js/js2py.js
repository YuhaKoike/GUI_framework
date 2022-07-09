//eel
function CameraNodeChange(id){
    var val = Number(document.getElementById(id).value)
    eel.CameraNodeChange(id, val);
}

//eel
function CameraControlBox(elem, cp){
    var center = document.createElement('center');
    var content = document.createElement('font');
    content.textContent = cp + ' Camera';

    var button1 = document.createElement('button');
    button1.textContent = 'R90';
    button1.id = cp + 'R90';
    button1.onclick = '';

    var button2 = document.createElement('button');
    button2.textContent = 'L90';
    button2.id = cp + 'L90';
    button2.onclick = '';

    var select = document.createElement('select');
    select.id = 'ColorSelect';
    select.onchange = function(){eel.RecordFunctions(this.value)};

    arr = ['Gray', 'Color'];
    for (const val of arr){
        var option = document.createElement('option');
        option.value = cp + val;
        option.text = val;
        select.appendChild(option);
    }

    center.appendChild(content);
    center.appendChild(button1);
    center.appendChild(button2);
    center.appendChild(select);

    var table = document.createElement('table');

    arr = ['Exposure', 'Gain', 'Framerate'];

    for (const val of arr){
        var newtr = document.createElement('tr');
        for (var i = 0; i < 3; i++){
            var newth = document.createElement('th');
            if (i == 0){
                newth.textContent = val;
            }
            else if (i == 1){
                var trackbar = document.createElement('input');
                trackbar.type = 'range';
                trackbar.id = cp + val + 'trackbar';
                trackbar.value = 0;
                trackbar.oninput = function(){CameraNodeChange(this.id)};
                newth.appendChild(trackbar);
            }
            else if (i == 2){
                var textbox = document.createElement('input');
                textbox.id = cp + val + 'textbox';
                textbox.value = 0;
                textbox.onchange = function(){CameraNodeChange(this.id)};
                newth.appendChild(textbox);
            }
            newtr.appendChild(newth);
        }
        table.appendChild(newtr);
    }
    center.appendChild(table);
    elem.appendChild(center);
}

//eel
function RecordBox(){
    var elem = document.getElementById('Record');

    var center = document.createElement('center');
    var content = document.createElement('font');
    content.textContent = 'Record and Capture';
    center.appendChild(content);

    var table = document.createElement('table');

    for (var j = 0; j < 3; j++){
        var newtr = document.createElement('tr');
        if (j == 0){
            for (var i = 0; i < 4; i++){
                var newth = document.createElement('th');
                if (i == 0){
                    newth.textContent = 'Record:';
                }
                else if (i == 1){
                    arr = ['Start', 'End', 'Cancel', 'Set'];
                    for (const val of arr){
                        var button = document.createElement('button');
                        button.id = val;
                        button.textContent = val;
                        if (val == 'Start'){
                            button.onclick = function(){eel.RecordFunctions(this.id);
                            lpcam = ['Bottom', 'Side'];
                            lf = ['Exposure', 'Gain', 'Framerate'];
                            lact = ['trackbar', 'textbox']
                            for (const pcam of lpcam){
                                for (const f of lf){
                                    for (const act of lact){
                                        e = document.getElementById(pcam + f + act);
                                        e.disabled = true;
                                    }
                                }
                            }

                            };
                        }
                        else if (val == 'End' || 'Cancel') {
                            button.onclick = function(){eel.RecordFunctions(this.id);
                                lpcam = ['Bottom', 'Side'];
                                lf = ['Exposure', 'Gain', 'Framerate'];
                                lact = ['trackbar', 'textbox']
                                for (const pcam of lpcam){
                                    for (const f of lf){
                                        for (const act of lact){
                                            e = document.getElementById(pcam + f + act);
                                            e.disabled = false;
                                        }
                                    }
                                }
    
                                };
                        }
                        else{
                            button.onclick = function(){eel.RecordFunctions(this.id);};
                        }
                        
                        newth.appendChild(button);
                    }
                    
                }
                else if (i == 2){
                    newth.textContent = 'Recorded Frame Num:';
                }
                else if (i == 3){
                    newth.textContent = 0;
                    newth.id = 'FrameCount';
                }
                newtr.appendChild(newth);
            }
        }
        else if (j == 1){
            for (var i = 0; i < 3; i++){
                var newth = document.createElement('th');
                if (i == 0){
                    newth.textContent = 'Folder';
                }
                else if (i == 1){
                    var textbox = document.createElement('input');
                    textbox.id = 'savefolder';
                    textbox.value = 'D:\\';
                    newth.appendChild(textbox);
                }
                else if (i == 2){
                    var button = document.createElement('button');
                    button.id = 'savefolderbutton';
                    button.textContent = 'Select';
                    button.onclick = function(){eel.SelectSaveFolder('savefolder');};
                    newth.appendChild(button);
                }
                newtr.appendChild(newth);
            }
        }
        else if (j == 2){
            for (var i = 0; i < 2; i++){
                var newth = document.createElement('th');
                if (i == 0){
                    newth.textContent = 'Capture';
                }
                else if (i == 1){
                    var button = document.createElement('button');
                    button.id = 'Capture';
                    button.textContent = 'Capture';
                    button.onclick = function(){eel.RecordFunctions(this.id)};
                    newth.appendChild(button);
                }
                newtr.appendChild(newth);
            }
        }
        table.appendChild(newtr);
    }
    center.appendChild(table);
    elem.appendChild(center);
}

//eel
function js2py(val, variable){
    eel.js2py(val, variable);
}