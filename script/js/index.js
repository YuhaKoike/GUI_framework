window.onload = function(){
    MakeCameraBox();
    MakeCalibrationBox();
}

function MakeCameraBox(){
    arr = ['Bottom', 'Side'];
    for (const val of arr){
        var elem = document.getElementById(val+'Cam');
        if (elem != null){
            CameraControlBox(elem, val);
        }
    }
    elem = document.getElementById('Record');
    if (elem != null){
        RecordBox();
    }
}

function MakeCalibrationBox(){
    elem = document.getElementById("Calibrationbox");
    if (elem == null){
        return;
    }
    var center = document.createElement('center');
    var text = document.createElement("font");
    text.textContent = "Setting Irradiation Area";
    center.appendChild(text);
    elem.appendChild(center);

    var text = document.createElement("font");
    text.textContent = "Calibration: ";
    elem.appendChild(text);

    var button = document.createElement("button");
    button.textContent = "Start";
    button.id = "calibrationStart";
    button.value = "True";
    button.onclick = function(){js2py(this.value,"calibrationStart");};
    elem.appendChild(button);

    arr = ["Input", "Output"];
    for (const val of arr){
        var button = document.createElement("button");
        button.textContent = val;
        button.id = "calibration" + val;
        button.value = "True";
        button.onclick = function(){eel.roi(this.id);};
        elem.appendChild(button);
    }

    var text = document.createElement("br");
    elem.appendChild(text);

    var text = document.createElement("font");
    text.textContent = "Coordinate: ";
    elem.appendChild(text);

    arr = ["x0", "x1", "y0", "y1"];
    for (const val of arr){
        var text = document.createElement("font");
        text.textContent = val + ": ";
        
        var input = document.createElement("input");
        input.type = "number";
        input.value = 0;
        input.id = "calib_" + val;
        input.onchange = function (){js2py(this.value, "calib_" + val)};
        input.style = 'width:50px; margin-right:5px; text-align: right';

        elem.appendChild(text);
        elem.appendChild(input);
    }
}
