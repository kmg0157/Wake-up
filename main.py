import cv2
import tensorflow.keras
import numpy as np
import winsound as ws
import requests
import json
import playsound

def beepsound():
    freq=440
    dur=2000
    ws.Beep(freq,dur)

def send_message():

    rest_api_key = 'rest_api_key' #rest api key입력
    redirect_uri = 'https://localhost.com' #redirect_url입력
    url_token = 'https://kauth.kakao.com/oauth/token'
    authorize_code = 'access token' #access token 입력

    try:
        with open("kakao_token.json", "r") as fp:  # 기존에 저장된 token 파일이 있는지 찾아봅니다.
            tokens = json.load(fp)
            if "error_code" in tokens:
                tokens = {}
    except Exception as e:
        print(e)
        tokens = {}

    if tokens == {}:
        param = {
            'grant_type': 'authorization_code',
            'client_id': rest_api_key,
            'redirect_uri': redirect_uri,
            'code': authorize_code,
        }

        response = requests.post('https://kauth.kakao.com/oauth/token', data=param)
        tokens = response.json()
        if "error_code" in tokens:
            print(tokens["error_code"])
        else:
            with open("kakao_token.json", "w") as fp:
                json.dump(tokens, fp)
                print("파일로 토큰 정보 저장!")
    else:
        headers = {
            "Authorization": "Bearer " + tokens["access_token"]
        }
        response = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers=headers)
        result = response.json()
        if "error_code" in result:
            param = {
                "grant_type": "refresh_token",
                "client_id": rest_api_key,
                "refresh_token": tokens["refresh_token"]
            }
            response = requests.post('https://kaluth.kakao.com/oauth/token', data=param)
            new_token = response.json()

            if "error_code" in new_token:
                print("ERROR :", new_token["error_code"])
            else:
                with open("kakao_token.json", "w") as fp:
                    json.dump(new_token, fp)
                    print("파일로 새로운 토큰 정보 저장")
        else:
            print("정상 토큰")

    with open("kakao_token.json", "r") as fp:
        tokens = json.load(fp)

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Authorization": "Bearer " + tokens["access_token"]
    }

    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "30초 이상 졸았습니다. 충분한 휴식을 취하세요.",
            "link": {
                "web_url": "https://www.youtube.com/watch?v=JNM3I4Q8wGU",
                "mobile_web_url": "https://www.youtube.com/watch?v=JNM3I4Q8wGU"
        },
            "button_title": "잠을 깨고 싶다면?"
        })
    }
    response = requests.post(url, headers=headers, data=data)
    print(response)
    playsound.playsound("kakaotalk_sound.mp3")

def preprocessing(frame):
    frame_fliped = cv2.flip(frame, 1)

    size = (224, 224)
    frame_resized = cv2.resize(frame_fliped, size, interpolation=cv2.INTER_AREA)

    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))

    return frame_reshaped

def predict(preprocessed):
    prediction=model.predict(preprocessed)
    return prediction


capture = cv2.VideoCapture(0)

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

model_filename = 'C:/Users/kmg01/project/wake-up/keras_model.h5'
model = tensorflow.keras.models.load_model(model_filename)

sleep_cnt = 1

while True:
    ret, frame = capture.read()

    if cv2.waitKey(500) > 0:
        break

    cv2.imshow("VideoFrame(Press any key!)", frame)

    preprocessed = preprocessing(frame)

    prediction = predict(preprocessed)

    if prediction[0, 0] > prediction[0, 1]:
        print("졸림 상태")
        sleep_cnt += 1
        if sleep_cnt % 15 == 0:
            sleep_cnt = 1
            beepsound()
            send_message()
    else:
        print("깨어있는 상태")
        sleep_cnt = 1

cv2.destroyAllWindows()