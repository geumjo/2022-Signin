from numpy import record
from tensorflow import keras
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import shutil

from trainning import *      # 학습 관련
from capture import *        # 촬영 관련
from predict import *        # 검증 관련
from Mysql import *          # sql
# from s3 import *

# 7인치 라떼판다 스크린 기준 해상도
# S3 사용 무시

Check_Page_Value = 0

# == style 정의를 위한 변수들 ==

# 기본 폰트
titleFont='italic'
contentFont='italic'

# 배경색 코드
bgcode='#003458'
fgcode='white'

# =============================

# 초기 페이지 정의

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Access Control')
        container = tk.Frame(self)
        self.attributes('-fullscreen', True)     # fullscreen
        self.resizable(False, False) #페이지 크기 고정
        self._frame = None
        self['bg'] = bgcode
        container.grid(column=0, row=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()


# 시작 페이지

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Start Page Open")
        self.master = master
        
        # Entry에서 입력 받은 값을 저장
        self.textbar = StringVar()
        self.admin_id_txt = StringVar()
        self.admin_pw_txt = StringVar()

        self['bg']=bgcode

        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=10, height=25)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="SIGN IN", fg=fgcode, bg=bgcode,
            font=(titleFont, 60, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(self, text="관리자용 로그인", fg=fgcode, bg=bgcode,
            font=(titleFont, 24, "bold")).place(x=150, y=230)
        
        # ID:
        tk.Label(self, text="ID :", fg=fgcode, bg=bgcode, font=(contentFont, 24)).place(x=500,y=130)
        admin_id = tk.Entry(self, width=20, textvariable=self.admin_id_txt, font=(contentFont, 24),
                ).place(x=600,y=130)
        # PW:
        tk.Label(self, text="PW :", fg=fgcode, bg=bgcode, font=('Ebrima', 24)).place(x=500,y=220)
        admin_pw = tk.Entry(self, width=20, textvariable=self.admin_pw_txt, show="*", font=(contentFont, 24),
                ).place(x=600,y=220)
        # 관리자 로그인 버튼
        tk.Button(self, text="로그인", fg=bgcode, bg=fgcode, width=10, font=(contentFont, 18),
            command=self.CheckAdmin).place(x=700,y=300)
        
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=1000)\
            .grid(row=0,column=2) # 출력을 위한 여백 (바 하나 있음 주의)
        
        # 밑줄
        canvas=tk.Canvas(self, width = 920, height = 30, bg=bgcode, bd = 0, highlightthickness = 0)
        line = canvas.create_line(0, 0, 920, 0, fill="white")
        canvas.place(x=20, y=400)


        # 근태 검사
        tk.Button(self, text="근태 검사 시작", fg=bgcode, bg=fgcode, font=(contentFont, 24), height=3,
                    command= self.Check_System, width=25).place(x=270, y=435)

        tk.Label(self, text="", fg=fgcode, bg=bgcode, font=(contentFont, 14),
            ).grid(row=6, column=1, pady=10)
        
        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=5, sticky="nsew") # 버튼 보이게 하기 위한 여백

    # 출퇴근검사 (예측함수실행)
    def Check_System(self):
        
        def stop():
            RecordPage.destroy()
            
        def close():
            RecordPage.destroy()
            self.Check_System()  
            
        def reTry():
            Dsql = "delete from record where num = (select max(num) from (select num from record) tmp);"
            sql1 = 'alter table record auto_increment=1;'
            sql2 = 'set @CNT=0;'   # num count 초기화
            sql3 = 'update record set record.num = @CNT:=@CNT+1;'  # num 고유번호 재정렬
            
            Process_SQL(Dsql, "commit")
            Process_SQL(sql1, "commit")
            Process_SQL(sql2, "commit")
            Process_SQL(sql3, "commit")
            print("Delete Record")
            
            RecordPage.destroy()
            self.Check_System() 
            
        Face_Predict(model) 
        
        sql1 = 'select * from record where num = (select max(num) from record);'
        result = Process_SQL(sql1, "select2")
        sql2 = 'select name from user where id = (select id from record where num = (select max(num) from record)) ;'
        name = Process_SQL(sql2, "select1")
        
        if name == "admin":
            name = "guest"
            
        RecordPage = tk.Tk()
        RecordPage.title("Access Check")
        RecordPage.attributes('-fullscreen', True)
        RecordPage['bg'] = bgcode
            
        tk.Label(RecordPage, text="", fg=fgcode, bg=bgcode, width=50, height=10).grid(row=0,column=0)
            
        tk.Label(RecordPage, text = "출입확인", fg=fgcode, bg=bgcode, font=(titleFont, 36, "bold")).place(x=420, y=50)
            
        tk.Label(RecordPage, text="이름: ", fg=fgcode, bg=bgcode, font=(contentFont, 18), pady=10).grid(row=1,column=1)
        tk.Label(RecordPage, text=name, fg=fgcode, bg=bgcode, font=(contentFont, 18)).grid(row=1,column=2)
            
        tk.Label(RecordPage, text="체온: ", fg=fgcode, bg=bgcode, font=(contentFont, 18), pady=10).grid(row=2,column=1)
        tk.Label(RecordPage, text=result[0][3], fg=fgcode, bg=bgcode, font=(contentFont, 18)).grid(row=2,column=2)
            
        tk.Label(RecordPage, text="출입시간: ", fg=fgcode, bg=bgcode, font=(contentFont, 18), pady=10).grid(row=3,column=1)
        tk.Label(RecordPage, text=result[0][2], fg=fgcode, bg=bgcode, font=(contentFont, 18)).grid(row=3,column=2)
            
        tk.Label(RecordPage, text="출입 상태: ", fg=fgcode, bg=bgcode, font=(contentFont, 18), pady=10).grid(row=4,column=1)
        tk.Label(RecordPage, text=result[0][4], fg=fgcode, bg=bgcode, font=(contentFont, 18)).grid(row=4,column=2)
            
        tk.Label(RecordPage, text="", bg=bgcode, height=2).grid(row=5)  # 여백     
            
        tk.Button(RecordPage, text="재시도", fg=bgcode, bg=fgcode, font=(contentFont, 18), command=reTry).grid(row=6, column=1)
            
        tk.Button(RecordPage, text="확인창닫기", fg=bgcode, bg=fgcode, font=(contentFont, 18), command=close).grid(row=6, column=2)
            
        tk.Button(RecordPage, text="검사 종료", fg=bgcode, bg=fgcode, font=(contentFont, 18), command=stop).place(x=460, y=500)
            
        
        # 관리자가 맞는지 체크
    def CheckAdmin(self):
        # 관리자 ID(admin)와 비밀번호(5538) 값 저장
        id = self.admin_id_txt.get()
        pw = self.admin_pw_txt.get()
        
        # 관리자 ID, 비밀번호 추출
        admin_id_db = "admin"
        if id == admin_id_db:
            sql = 'select password from user where name="admin";'
            admin_pw_db = Process_SQL(sql, "select1")
            self.textbar.set("확인 중입니다...")

            # 최종 확인(id, pw 모두 일치)  --> 영상 촬영 시작
            if pw == admin_pw_db:
                self.textbar.set("확인되었습니다. 잠시만 기다려주세요...")
                time.sleep(1)
                self.master.switch_frame(AdminPage)
            else:
                print("Not Collect Password")
                self.textbar.set("비밀번호가 일치하지 않습니다.")
        else:
            print("Not Collect Admin ID, Retry")
            self.textbar.set("관리자 정보와 일치하지 않습니다. 다시 한번 입력하세요.")


# 관리자 권한 페이지

class AdminPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Admin Page Open")
        self.master = master
        
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=25, height=12)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="관리자 페이지", fg=fgcode, bg=bgcode,
            font=(titleFont, 40, "bold")).grid(row=0, column=1, pady=5)
        
        # 밑줄
        canvas=tk.Canvas(self, width = 400, height = 30, bg=bgcode, bd = 0, highlightthickness = 0)
        line = canvas.create_line(0, 0, 400, 0, fill="white")
        canvas.place(x=300, y=200)

        # 신규 등록
        tk.Button(self, text="신규 유저 등록 및 촬영", fg=bgcode, bg=fgcode, font=(contentFont, 20), width=40,
                command=lambda: master.switch_frame(NewUserPage)).grid(row=1, column=1, pady=5, ipady=3)
        
        # 기존 유저 추가
        tk.Button(self, text="기존 유저 데이터 추가", fg=bgcode, bg=fgcode, font=(contentFont, 20),
                    command=lambda: master.switch_frame(AddUserImagePage), width=40).grid(row=2, column=1, pady=5, ipady=3)

        # 회원 삭제
        tk.Button(self, text="유저 삭제", fg=bgcode, bg=fgcode, font=(contentFont, 20), width=40,
                command=lambda: master.switch_frame(DeletePage)).grid(row=3, column=1, pady=5, ipady=3)

        #얼굴 이미지 학습
        tk.Button(self, text="학습시키기", fg=bgcode, bg=fgcode, font=(contentFont, 20), width=40,
                command=self.ask_training).grid(row=4, column=1, pady=5, ipady=3)


        # 로그인 페이지로 돌아가기
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, font=(contentFont, 14), width=10,
                command=lambda: master.switch_frame(StartPage)).grid(row=5, column=1, pady=30, ipady=3)
        self['bg']=bgcode

        #tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=6, sticky="nsew") # 로고 보이게 하기 위한 여백


    def ask_training(self):
        MsgBox=tk.messagebox.askokcancel("Training", "학습을 시작합니다.\n(확인 버튼 클릭 시 시작)")
        
        if MsgBox==True:
            try:
                Training_Start()
                tk.messagebox.showinfo("Success", "완료되었습니다.")
            except:
                self.re_training()
        else:
            tk.messagebox.showinfo("Cancel", "취소되었습니다.")

    def re_training(self):
        MsgBox=tk.messagebox.askretrycancel("ERROR","사진파일 확인 후 다시 시도 하십시오.")
        
        if MsgBox==True:
            self.ask_training()
        else:
            tk.messagebox.showinfo("Cancel", "취소되었습니다.")


# 신규 사용자 등록 페이지

class NewUserPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("NewUser Page Open")
        self.master = master

        # 신규 사용자 ID, PW 저장
        self.newid = StringVar()
        self.newpw = StringVar()
        self.phone = StringVar()
        self.infotext = StringVar()
        self.check = tk.BooleanVar()

        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=24, height=10)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="신규 유저 등록", fg=fgcode, bg=bgcode,
            font=(titleFont, 36, "bold")).grid(row=0, column=2, pady=5)

        # New ID:
        tk.Label(self, text="New ID :", fg=fgcode, bg=bgcode, font=(contentFont, 18))\
            .grid(row=1, column=1, pady=3)
        user_id = tk.Entry(self, width=30, textvariable=self.newid, font=(contentFont, 18))\
            .grid(row=1, column=2, pady=10, ipady=5)
        
        # New PW:
        tk.Label(self, text="New PW :", fg=fgcode, bg=bgcode, font=(contentFont, 18))\
            .grid(row=2, column=1, pady=5)
        user_pw = tk.Entry(self, width=30, textvariable=self.newpw, show="*", font=(contentFont, 18))\
            .grid(row=2, column=2, pady=10, ipady=5)
            
        # phone number
        tk.Label(self, text="phone(no'-') :", fg=fgcode, bg=bgcode, font=(contentFont, 18))\
            .grid(row=3, column=1, pady=5)
        phone_num = tk.Entry(self, width=30, textvariable=self.phone, font=(contentFont, 18))\
            .grid(row=3, column=2, pady=10, ipady=5)

        tk.Button(self, text="등록 및 촬영", fg=bgcode, bg=fgcode, width=20, font=(contentFont, 20),
            command=self.SignUp).grid(row=4, column=2, pady=20)
        
        
        
        def consent():
            tk.messagebox.showinfo("개인정보의 수집·이용에 관한 사항 및 동의",
                                   "□ 개인정보의 수집·이용 목적\n- 본 시스템을 지원하기 위한 정보수집\n□ 수집하려는 개인정보의 항목\n- 성명, 연락처, 얼굴 사진\n□ 개인정보의 보유 및 이용기간\n- 본 프로젝트 수행 기간\n□ 본 시스템을 이용하기 위해선 개인정보의 수집·이용 동의를 거부할 수 있으며, 거부할 경우에는 본 시스템을 이용할 수 없습니다.")
        
        checkbutton=tk.Checkbutton(self, text="개인정보 수집 동의", font=(contentFont, 18), var=self.check, command=consent)
        checkbutton.grid(row= 5, column=2)
        
        
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 18),
            command=lambda: master.switch_frame(AdminPage)).grid(row=6, column=2, pady=20)

        tk.Label(self, text="", fg=fgcode, bg=bgcode, textvariable=self.infotext).grid(row=7, column=2, pady=3)       
        self['bg']=bgcode

    
    # 사용자 계정 등록 및 사진촬영
    def SignUp(self):
        
        if self.check.get() == False:
            self.infotext.set("개인정보 수집 동의를 해주세요!")
            print("Check Please!")
            return 0
        
        id = self.newid.get()
        pw = self.newpw.get()
        pno = self.phone.get()
        role = "USER"
        reg = datetime.datetime.now()
        reg = str(reg)
        # ID, PW가 일치하는 기존 사용자가 있는지 검사
        sql1='select id from user where name="' + id + '" and password="' + pw + '";'
        try:
            sql1_result = Process_SQL(sql1, "select1")
            print("User Already Exists.")
            self.infotext.set("User Already Exists.")
        except:
            sql2 = 'insert into user(name, password, registration, role, phone) values("' + id + '","' + pw + '","' + reg + '","' + role + '","' + pno + '");'
            sql3 = 'set @CNT=0;'   # id count 초기화
            sql4 = 'update user set user.id = @CNT:=@CNT+1;'  # id 고유번호 재정렬
            Process_SQL(sql2, "commit")
            Process_SQL(sql3, "commit")
            Process_SQL(sql4, "commit")
            sql1_result = Process_SQL(sql1, "select1")

            # 신규 사용자 이미지 저장 폴더 생성 후 캡처 진행
            Image_Route = "./image/" + str(sql1_result)
            try:
                if not os.path.exists(Image_Route):
                    os.makedirs(Image_Route)
            except OSError:
                print("Error Making Image Folder!")

            self.infotext.set("등록되었습니다. 촬영이 시작됩니다...")
            print("New User Is Saved")

            # 얼굴 촬영 함수 시작
            Face_Capture(sql1_result)
            tk.messagebox.showinfo("Success", "완료되었습니다.")
    
    



# 회원 삭제 페이지

class DeletePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Delete Page Open")
        self.master = master
        self.textbar = StringVar()
        self.userid = StringVar()
        self.userpw = StringVar()

        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=27, height=15)\
            .grid(row=0, column=0) # 가운데 정렬용
        tk.Label(self, text="유저 정보 삭제", fg=fgcode, bg=bgcode,
            font=(titleFont, 40, "bold")).grid(row=0, column=2)
        self['bg']=bgcode

        # 회원 조회
        tk.Label(self, text="User ID :", fg=fgcode, bg=bgcode, font=(contentFont, 24), pady=5).grid(row=1, column=1, pady=5)
        tk.Label(self, text="User PW :", fg=fgcode, bg=bgcode, font=(contentFont, 24), pady=5).grid(row=2, column=1, pady=5)

        user_id = tk.Entry(self, width=20, textvariable=self.userid, font=(contentFont, 20)).grid(row=1, column=2, pady=3, ipady=5)
        user_pw = tk.Entry(self, width=20, textvariable=self.userpw, show="*", font=(contentFont, 20)).grid(row=2, column=2, pady=3, ipady=5)

        tk.Button(self, text="삭제", fg=bgcode, bg=fgcode, width=10, font=(contentFont, 20),
            command=self.delete).grid(row=3, column=2, pady=15, ipady=2)
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 18),
            command=lambda: master.switch_frame(AdminPage)).grid(row=5, column=2, pady=20)

        tk.Label(self, text="", fg=fgcode, bg=bgcode, textvariable=self.textbar).grid(row=6, column=2, pady=3)
        

    # 회원 삭제 함수
    def delete(self):
        id = self.userid.get()
        pw = self.userpw.get()
        sql = 'select id from user where name="' + id + '" and password="' + pw + '";'
        
        # 등록된 사용자인지 확인 후 고유 번호 획득 --> 삭제 진행
        try:
            sql_result = Process_SQL(sql, "select1")   # 고유번호 (id)
            self.textbar.set("삭제되었습니다.")
            print(sql_result)

            # 삭제
            Dsql = "delete from user where id=" + str(sql_result) + ";"
            sql3 = 'set @CNT=0;'   # id count 초기화
            sql4 = 'update user set user.id = @CNT:=@CNT+1;'  # id 고유번호 재정렬
            Process_SQL(Dsql, "commit")
            Process_SQL(sql3, "commit")
            Process_SQL(sql4, "commit")
            print("User Delete Complete !")

            # 이미지 저장 폴더 삭제
            Image_Route = './image/' + str(sql_result)
            shutil.rmtree(Image_Route)
            print("Image Folder Deleted!!")
            
        except:
            print("Not Collect User ..!")
            self.textbar.set("아이디 또는 비밀번호가 일치하지 않습니다.")

# 기존 회원 사진촬영

class AddUserImagePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("추가 사진 등록")
        self.master = master
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=30, height=15).grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="회원 조회", fg=fgcode, bg=bgcode, font=(titleFont, 40, "bold")).grid(row=0, column=2, pady=5)
        
        tk.Label(self, text="User ID :", fg=fgcode, bg=bgcode, font=(contentFont, 24), pady=5).grid(row=1, column=1, pady=5)
        tk.Label(self, text="User PW :", fg=fgcode, bg=bgcode, font=(contentFont, 24), pady=5).grid(row=2, column=1, pady=5)

        self.textbar = StringVar()
        self.userid = StringVar()
        self.userpw = StringVar()

        user_id = tk.Entry(self, width=20, textvariable=self.userid, font=(contentFont, 20)).grid(row=1, column=2, pady=3, ipady=5)
        user_pw = tk.Entry(self, width=20, textvariable=self.userpw, show="*", font=(contentFont, 20)).grid(row=2, column=2, pady=3, ipady=5)

        tk.Button(self, text="촬영", fg=bgcode, bg=fgcode, width=10, font=(contentFont, 20),
            command=self.SignIn).grid(row=3, column=2, pady=15, ipady=2)
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 18),
            command=lambda: master.switch_frame(AdminPage)).grid(row=5, column=2, pady=20) 

        tk.Label(self, text="", fg=fgcode, bg=bgcode, textvariable=self.textbar).grid(row=6, column=2, pady=3)     
        self['bg']=bgcode




    # 사용자 로그인 및 추가 작업
    def SignIn(self):
        id = self.userid.get()
        pw = self.userpw.get()
        sql = 'select id from user where name="' + id + '" and password="' + pw + '";'
        
        # 등록된 사용자인지 확인 후 고유 번호 획득 --> 촬영 진행
        try:
            sql_result = Process_SQL(sql, "select1")
            self.textbar.set("조회되었습니다. 촬영을 시작합니다...")
            print(sql_result)
            Face_Capture(sql_result)
        except:
            print("Not Collect User Access..!")
            self.textbar.set("아이디 또는 비밀번호가 일치하지 않습니다.")


if __name__ == "__main__":
    model = keras.models.load_model('./trainer/Save_model')
    print("Page is Open")
    app = SampleApp()
    app.mainloop()