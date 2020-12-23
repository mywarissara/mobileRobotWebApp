from django.http import HttpResponse , StreamingHttpResponse ,request
from django.shortcuts import redirect
from django.shortcuts import render
from mobile.facereg import *
import numpy

def index(request):
    return render(request,'mobile/index.html')

def setting(request):
    return render(request,'mobile/setting.html')

import json
  
_name = ''
_no = 1
isSnapComplete = 0
number_pic = 30
isHuman = 0
i = 0
def register(request):
    global _name
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        role = request.POST.get('role')
        news = request.POST.get('news')
        info = {
            "user": [{
            "name": name,
            "surname" : surname,
            "email": email,
            "role": role,
            "news": news,
        }]}
        _name = info['user'][0]['name']
        print(_name)
        with open('users.json') as json_file:
            data = json.load(json_file)
            if data != '':
                data['user'].append(info)
                info = data
            else:
                pass

        with open('users.json', 'w') as json_file:
            json.dump(data, json_file)
        return redirect('/facereg')
    return render(request,'mobile/register.html')


def get_user_info(request):
    with open('users.json') as json_file:
            data = json.load(json_file)
            print(data['user'][1:])
    return HttpResponse(json.dumps(data), content_type="application/json")

def take_picture(request):
    return render(request,'mobile/take_picture.html')

def admin(request):
    return render(request,'mobile/admin.html')

def save_point(request):
    return render(request,'mobile/save_point.html')

def complete(request):
    return render(request,'mobile/complete.html')
  
def counter(request):
    return HttpResponse(isSnapComplete)


def snapshot(request):
    global _no, isSnapComplete, isHuman, _name, globalImage
    path_curr = os.getcwd()  # get current Dir
    # print('me:'+ str(isHuman))

    path_pic = path_curr + "/mobile/static/page_mobile/knn_examples/train/" + _name
    try:
        os.mkdir(path_pic)
    except:
        print("[Warning] The folder already existed!")

    if isSnapComplete == 0 and isHuman != 0:
        name_file = _name + "_face_" + str(_no)
        image_file = path_pic + "/" + name_file + ".png"
        globalImage = cv2.resize(
            globalImage, (globalImage.shape[1]//2, globalImage.shape[0]//2), interpolation=cv2.INTER_AREA)

        cv2.imwrite(image_file, globalImage)
        if _no%number_pic == 0:
            isSnapComplete = 1
            _no = 0
        else: 
            isSnapComplete = 0
            _no += 1

        return HttpResponse('ok')
    elif isSnapComplete == 1:
        print('train')
        path_curr = os.getcwd()  # get current Dir
        path_pic = path_curr + "/mobile/static/page_mobile/knn_examples/train/"
        create_new_model(path_pic)

        return HttpResponse('success')
    else:
        return HttpResponse('not human detected')


import cv2
globalImage = None

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        global globalImage, isHuman
        _,image = self.video.read()
        globalImage = image.copy()  
        image, isHuman = take_pic("input", image)
        print(isHuman)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_frame_to_predict(self):
        global globalImage
        _,image = self.video.read()
        globalImage = image.copy()  
        image, predicted_name = face_detection_main(image)
        if predicted_name != 'unknown':
            print(predicted_name)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def video_generator(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_generator_predict(camera):
    while True:
        frame = camera.get_frame_to_predict()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def camera_live(request):
    try:
        return StreamingHttpResponse(video_generator(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  
        pass

def camera_live_to_predict(request):
    try:
        return StreamingHttpResponse(video_generator_predict(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  
        pass