var ipadd = "172.16.10.20:8000"

function sendPoint(no) {
    console.log("[INFO] Send Point Active")
    console.log('send point' + String(no));
    fetch('http://' + ipadd + '/api/getConnection')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data == 1) {
                doSendPoint(no);
            }
            else if (data == 0) {
                console.log('error on web socket')
            }
            else {
                console.log('error')
            }
        });
}

function doSendPoint(no) {
    var point = { "location_index": no }

    fetch('http://' + ipadd + '/api/moveBasePoint', {
        method: 'POST', // or 'PUT'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(point),
    })
        .then(response => response.text())
        .then(b => {
            console.log('Success:', b);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}



function save_point() {
    fetch('http://' + ipadd + '/api/getConnection')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data == 1) {
                save_point_true();
            }
            else if (data == 0) {
                document.getElementById('label-save-point').innerHTML = 'Error on web socket'
            }
            else {
                document.getElementById('label-save-point').innerHTML = 'Error'

            }
        });

}
var pose_update;
function save_point_true() {
    a =
    {
        "name": "Robotic Lab",
        "poseMessage":
        {
            "targetPose":
            {
                "header":
                {
                    "frame_id": "map",
                },
                "Pose": {}
            }
        }
    }
    console.log('save point');
    fetch('http://' + ipadd + '/api/getPose')
        .then(response => response.json())
        .then(data => {
            placeName = document.getElementById('place').value;
            console.log(placeName);
            document.getElementById('label-save-point').innerHTML = 'Success to save this position at ' + placeName;
            a.poseMessage.targetPose.Pose = data;
            a.name = placeName;

            JSON.stringify(a);

            fetch('http://' + ipadd + '/api/savePoint', {
                method: 'POST', // or 'PUT'
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(a),
            })
                .then(response => response.text())
                .then(b => {
                    console.log('Success:', b);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

        });
}
var fb;

function show_info() {
    fetch('http://localhost:8080/get_user_info')
        // .then(response => response.json())
        .then(response => response.json())
        .then(data => {
            // console.log(data['user']['0']['user']['0']['name']);
            fb = data;
            console.log(fb)

        });

}

var mobileRowSelected;
var mobileCellSelected;
var on_mobileRow = false;

function refreshUsers() {
    highlight_row();
    fetch('http://localhost:8080/get_user_info')
        // .then(response => response.json())
        .then(response => response.json())
        .then(data => {
            // console.log(data['user']['0']['user']['0']['name']);
            var noUsers = data['user'].length;
            console.log(noUsers)
            for (i = 0; i < noUsers; i++) {
                let table = document.getElementById("mobile_table");
                let row = table.insertRow();
                let cell1 = row.insertCell(0);
                let cell2 = row.insertCell(1);
                let cell3 = row.insertCell(2);
                let cell4 = row.insertCell(3);

                // (table.getElementsByTagName("tr"))[i].style.backgroundColor = "#000";
                // (table.getElementsByTagName("tr"))[i].style.color = "#000";
                // (table.getElementsByTagName("tr"))[i].style.border = "collapse";

                row.id = i;
                noRow = String(i);

                console.log(noRow);
                cell1.innerHTML = data['user'][noRow]['user']['0']['name'];
                cell2.innerHTML = data['user'][noRow]['user']['0']['surname'];
                cell3.innerHTML = data['user'][noRow]['user']['0']['email'];
                cell4.innerHTML = data['user'][noRow]['user']['0']['role'];
            }
        });
}
var is_selectTable = 0;
var on_mobileRow = false;
function highlight_row() {
    var table = document.getElementById("mobile_table");
    var cells = table.getElementsByTagName('td');
    for (let i = 0; i < cells.length; i++) {
        // Take each cell
        var cell = cells[i];
        // do something on onclick event for cell
        cell.onclick = function () {
            on_mobileRow = true;

            // Get the row id where the cell exists
            var rowId = this.parentNode.rowIndex;

            var rowsNotSelected = table.getElementsByTagName('tr');
            for (var row = 0; row < rowsNotSelected.length; row++) {
                rowsNotSelected[row].style.backgroundColor = "#eee";
                rowsNotSelected[row].style.color = "#000";
                rowsNotSelected[row].classList.remove('selected');
            }
            var rowSelected = table.getElementsByTagName('tr')[rowId];
            rowSelected.style.backgroundColor = "#888";
            rowSelected.style.color = "#000";
            rowSelected.className += " selected";

            mobileRowSelected = rowSelected.cells[0].innerHTML;
            mobileCellSelected = this.innerHTML;
            is_selectTable = 1;
        }
    }
}

function mobileDelRow() {
    var array = [1, 2, 3, 4];
    var evens = _.remove(array, function (n) {
        return n % 2 === 0;
    });
    console.log(array);

}


var ipadd = "172.16.10.20:8000"
var k = 0;
function addBtn() {
    pArray = [];
    // pArray = get_point_list();
    fetch('http://' + ipadd + '/api/loadPoint')
        .then(response => response.json())
        .then(data => {
            pArray = data;

            // pArray = ['a', 'b', 'c', 'd'];
            pArray.push(" ");

            var count = 0;
            var stop = false;
            // ['','','']
            var length = pArray.length;
            length -= 1
            count = length / 3;
            count = Math.ceil(count);
            console.log(pArray);
            console.log(count);

            if (pArray != [] && stop == false) {
                for (var i = 0; i < count; i++) {
                    var btnColumn = document.createElement("DIV");
                    btnColumn.className += 'carousel-item';
                    console.log('add i');
                    if (i == 0) {
                        btnColumn.className += ' active';
                    }
                    for (var j = 0; j < 3; j++) {
                        console.log(k);
                        var btnItem = document.createElement("DIV");
                        btnItem.className += 'col-xs-3 ';
                        btnItem.className += 'col-sm-3 ';
                        btnItem.className += 'col-md-3 ';

                        var button = document.createElement('BUTTON');
                        var text = document.createTextNode(pArray[k]);
                        // text.style.color = 'black'
                        button.appendChild(text);
                        btnItem.appendChild(button);
                        btnColumn.appendChild(btnItem);

                        button.id = String(k)
                        button.className += 'btn ';
                        button.className += 'btn-outline-light ';
                        button.className += 'btn-size';
                        button.onclick = function sendPoint() {
                            console.log("[INFO] Send Point Active");
                            var pointNumber = button.id
                            console.log('send point' + String(this.id));
                            fetch('http://' + ipadd + '/api/getConnection')
                                .then(response => response.json())
                                .then(data => {
                                    console.log(data);
                                    if (data == 1) {
                                        var point = { "location_index": pointNumber }

                                        fetch('http://' + ipadd + '/api/moveBasePoint', {
                                            method: 'POST', // or 'PUT'
                                            headers: {
                                                'Content-Type': 'application/json',
                                            },
                                            body: JSON.stringify(point),
                                        })
                                            .then(response => response.text())
                                            .then(b => {
                                                console.log('Success:', b);
                                            })
                                            .catch((error) => {
                                                console.error('Error:', error);
                                            });
                                    }
                                    else if (data == 0) {
                                        console.log('error on web socket')
                                    }
                                    else {
                                        console.log('error')
                                    }
                                });
                        }
                        
                        // sendPoint.setAttribute("onclick", "addBtn()");
                        // getElementById('button-sendPoint').onclick = sendPoint(k);
                        if (k - (length-1) < 0) {
                            k += 1;
                            stop = true;
                        }

                    }
                    document.getElementById("btn-container").appendChild(btnColumn);
                }
            }
        });
}

var point = [];
function get_point_list() {
    console.log("get p")
    fetch('http://' + ipadd + '/api/loadPoint')
        .then(response => response.json())
        .then(data => {
            point = data;
            console.log(data)
        });
    return point

}
