from tensorflow import keras
import numpy as np
import os
from sklearn.model_selection import train_test_split
from PIL import Image

from Mysql import *
# from s3 import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#      학습 모델을 위한 폴더 경로 설정 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def Training_Start():
    # ---------------------------
    #    path = 사진 학습 경로    
    #     필히 이름과 경로 확인   
    # ---------------------------
    path = r'./image'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~ 회원 클래스 리스트 가져오기 ~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # DB에서 1번은 관리자로 지정함
    sql = 'select name from user where id>1;'
    sql_result = Process_SQL(sql, "select2")

    # ['Unknown', '사용자1', '사용자2', '사용자3', ...] 리스트 저장
    classes = ['Unknown']
    for name in sql_result:
        classes.append(name[0])

    num_classes = len(classes)

    # 사진이 저장된 회원 클래스 리스트 가져오기
    classes_id = [f for f in os.listdir(path)]
    classes_id.sort()

    img_w = 68  # 배열 = pixels
    img_h = 68 
    X = []      # image pixels 
    Y = []      # Label
    
    for idx, class_value in enumerate(classes_id):
        ImageDir = path + '/' + class_value   # 클래스의 이미지 저장된 폴더
        files = [os.path.join(ImageDir,f) for f in os.listdir(ImageDir)]

        for f in files:
            img = Image.open(f)
            img_numpy = np.array(img, 'uint8') / 255.0  # 소수점 값 배열
            X.append(img_numpy)
            Y.append(int(class_value))

    #  CNN 학습 모델 매핑을 위한 Numpy 및 재구성
    X = np.array(X).reshape(-1, 68, 68, 1)
    Y = np.array(Y, 'uint8')

    # 학습, 검증 모델 구현 (8:2)
    print("Training Model Create...")   

    train_scaled, val_scaled, train_target, val_target =\
        train_test_split(X, Y, test_size=0.1, random_state=30)

    model = keras.Sequential()

    model.add(keras.layers.Conv2D(32, kernel_size=5, activation='relu',
                            padding='same', input_shape=(68, 68, 1)))

    # 풀링 크기 (2, 2) 지정
    model.add(keras.layers.MaxPooling2D(2))


    model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu', padding='same'))
    model.add(keras.layers.MaxPooling2D(2))
    model.add(keras.layers.Dropout(0.25))    
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(200, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    # 클래스 개수만큼 분류하는 소프트맥스 활성화 함수
    model.add(keras.layers.Dense(num_classes+1, activation='softmax'))

    model.summary()

    # sparse_categorical_crossentropy
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # 최적 학습 모델 저장
    check_cb = keras.callbacks.ModelCheckpoint('./trainer/Save_Model/best-cnn-model.h5')

    early_stop = keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)

    history = model.fit(train_scaled, train_target, epochs=20,
                    validation_data=(val_scaled, val_target), callbacks=[check_cb, early_stop])

    model.evaluate(val_scaled, val_target)

    model.save('./trainer/Save_Model')
    #s3_upload()
    print("Training Completed!!!")


    # 검증
    # model.evaluate(val_scaled, val_target)

Training_Start()