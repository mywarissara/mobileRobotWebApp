function save_point() {
    // fetch('http://172.16.10.20:8000/api/getPose')
    fetch('http://172.16.10.20:8000/api/getConnection')
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
    fetch('http://172.16.10.20:8000/api/getPose')
        .then(response => response.json())
        .then(data => {
            placeName = document.getElementById('place').value;
            document.getElementById('label-save-point').innerHTML = 'Success to save this position at ' + placeName;
            a.poseMessage.targetPose.Pose = data;
            JSON.stringify(a);

            fetch('http://172.16.10.20:8000/api/savePoint', {
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
