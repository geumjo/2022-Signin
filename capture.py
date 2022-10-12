import cv2
import cvlib as cv
import time
#from s3 import *

# 얼굴 이미지 조정
def resizeImage(frame):
    size = (68, 68) # 68 X 68
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    return frame_resized


# 촬영 및 저장
# 저장 경로 확인 : s3 :: signinbucket1/image/ ...
def Face_Capture(id_num):
    count = 0    # 캡처 프레임 개수 cnt
    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    webcam.set(3, 1300) # video width
    webcam.set(4, 500) # video height
    
    # 카메라 정상 작동 오류 발생 시에
    if not webcam.isOpened():
        print("Could not open webcam")
        exit()

    # 카메라 촬영 루프
    while webcam.isOpened():
        # 촬영 시간 값 저장
        time_set = int(time.strftime("%y%m%d%H%M%S"))

        # 카메라 프레임 저장 (status - 정상(True), 에러(False)) 
        status, frame = webcam.read()
        
        count = count + 1
        if not status:
            print("Cam is not working")
            break

        # face: 확인한 얼굴 부분의 좌표
        # confidences: 확률 
        face, confidence = cv.detect_face(frame)
    
        # 처리 상태 확인 (기본 주석)
        # print(face)
        # print(confidence)
        
        
        # 일정 촬영 횟수에 다다르면 종료
        # 종료 이후 사진 학습 진행
        if count>=500:
            print(f"Capture is Completed!!")
            webcam.release()
            cv2.destroyAllWindows()
            break

        # 얼굴 판별 및 사진 저장 루프
        for idx, f in enumerate(face):
            (startX, startY) = f[0], f[1]
            (endX, endY) = f[2], f[3]
        
            # 시작 좌표, 끝 좌표, 사각형 선 색상, 두께
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)
            
            cv2.putText(frame, f"Look at the camera; count: {count}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "Please turn your head in diffrent directions", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 8번 정상 캡쳐시 진행
            if count % 8  == 0:                     
                face_in_img = frame[startY:endY, startX:endX]
                face_in_img = cv2.cvtColor(face_in_img, cv2.COLOR_BGR2GRAY)
                img = resizeImage(face_in_img)
                
                # 로컬 저장
                filename = './image/' + str(id_num) + '/User_' + str(id_num) + '_' + str(time_set) + '.jpg'
                cv2.imwrite(f"{filename}", img)
                # cv2.imwrite('./image/' + str(id_num) + '/User_' + str(id_num) + '_' + str(time_set) + '.jpg', img)
                print(f"Capture Complete :{count}")

                # S3 업로드
                # s3_upload()


        # 영상 화면 출력
        cv2.imshow("captured frames", frame)
    
        # 'ESC' 누르면 종료
        # 종료 이후에 사진 학습 진행
        k = cv2.waitKey(10) & 0xff 
        if k == 27:
            webcam.release()
            cv2.destroyAllWindows()
            break
