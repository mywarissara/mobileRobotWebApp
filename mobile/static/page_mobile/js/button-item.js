var ipadd = "172.16.10.20:8000"
var k = 0;
function addBtn() {
    pArray = [];
    // pArray = get_point_list();
    pArray = ['a', 'b', 'c', 'd'];
    var count = 0;
    var stop = false;
    // ['','','']
    var length = pArray.length;
    count = length / 3;
    count = Math.ceil(count);
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
                console.log('add j');
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
                button.className += 'btn ';
                button.className += 'btn-outline-light ';
                button.className += 'btn-size';
                if (k < (length)) {
                    k += 1;
                    stop = true;
                }
                if (k == (length - 2)) {
                    pArray.push(" ");
                }
            }
            document.getElementById("btn-container").appendChild(btnColumn);

        }
    }


}

var point = [];
function get_point_list() {
    // console.log("get p")

    fetch('http://' + ipadd + '/api/loadPoint')
        .then(response => response.json())
        .then(data => {
            point = data;
        });
    return point

}
