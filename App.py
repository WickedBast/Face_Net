import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk, filedialog
import pytz
from google.auth.exceptions import RefreshError
from tkcalendar import Calendar
from datetime import date
from datetime import datetime
from datetime import timedelta
from gaze_tracking import GazeTracking
import pyrebase
import cv2
from pathlib import Path
import face_recognition
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import pandas as pd
import numpy as np
import requests
from threading import *
import time
import shutil
from firebase_admin import storage as admin_storage
import pytesseract
import threading
import webbrowser
from PIL import ImageTk, Image

#sdsddsdssdds
firebaseConfig = {
    "apiKey": "AIzaSyCGHyT8asvQwZUGZtpIbTYRozvLYaHBqPo",
    "authDomain": "facenet-f0615.firebaseapp.com",
    "projectId": "facenet-f0615",
    "storageBucket": "facenet-f0615.appspot.com",
    "messagingSenderId": "980866370515",
    "appId": "1:980866370515:web:54e0051f45a181045a3d26",
    "measurementId": "G-HY8XHELYPL",
    "databaseURL": "https://facenet-f0615-default-rtdb.firebaseio.com/"
}

cred = credentials.Certificate('firebase-admin-sdk.json')
admin = firebase_admin.initialize_app(cred, {"databaseURL": "https://facenet-f0615-default-rtdb.firebaseio.com/",
                                             "storageBucket": "facenet-f0615.appspot.com"})
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth1 = firebase.auth()
storage = firebase.storage()
encodelist = ()


# MAIN APP


class FaceNet(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.shared_data = {
            "email": tk.StringVar(),
            "selectedCourse": tk.StringVar(),
            "selectedExam": tk.StringVar()
        }

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (
                Login, StudentRegister, TeacherRegister, ForgotPassword, TeacherMainPage, StudentMainPage,
                CreateCourse, DeleteCourse, CreateExam, DeleteExam, CourseDetailPage, ExamDetailPage,
                ExamDetailStudent, ExamPageS, CoursePageS, TeacherCoursePage, ExamReports):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Login)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_frame(self, page_name):
        frame = self.frames[page_name]
        return frame


# SHARED PAGES


class Login(tk.Frame):
    # TODO: ADD LOGO
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def login():
            if str(email.get()).isspace() or str(password.get()).isspace():
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(email.get())) == 0 or len(str(password.get())) == 0:
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif not str(email.get()).endswith("@isik.edu.tr" or not str(email.get()).endswith("@isikun.edu.tr")):
                messagebox.showerror("Wrong Email", "Please enter your Işık University Email.")
            else:
                try:
                    User = auth.get_user_by_email(str(email.get())).email_verified

                    if User:
                        auth1.sign_in_with_email_and_password(str(email.get()), str(password.get()))
                        password.delete(0, 'end')
                        if str(email.get()).endswith("@isikun.edu.tr") or str(email.get()) == "korhan.koz@isik.edu.tr":
                            global welcomeMessage
                            welcomeMessage.set("Welcome " + self.controller.shared_data["email"].get())
                            controller.get_frame(TeacherMainPage).courses()
                            controller.show_frame(TeacherMainPage)
                        else:
                            global welcomeMessageStudent
                            welcomeMessageStudent.set("Welcome " + self.controller.shared_data["email"].get())
                            controller.get_frame(StudentMainPage).coursesS()
                            controller.show_frame(StudentMainPage)
                    else:
                        messagebox.showerror("Email Not Verified or Not Registered", "Please check your email")
                except requests.exceptions.HTTPError:
                    messagebox.showerror("Information Credentials", "Your email or password is wrong")
                except RefreshError:
                    messagebox.showerror("Check Date and Time", "Check your PC's date and time")
                except:
                    messagebox.showerror("Information Credentials", "Your email or password is wrong")

        def refresh():
            email.bind("<FocusIn>", lambda args: email.delete(0, 'end'))
            password.bind("<FocusIn>", lambda args: password.delete(0, 'end'))

        def backS():
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            t1 = Thread(target=controller.get_frame(StudentRegister).cardReader)
            t1.start()
            controller.get_frame(StudentRegister).enable()
            controller.show_frame(StudentRegister)

        def backT():
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            controller.show_frame(TeacherRegister)

        welcome = Label(self, text=" SIGN IN ", width=150, height=10, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

        emailL = Label(self, text="E-mail:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        emailL.grid(row=5, column=0, columnspan=3, padx=10, pady=20)

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF",
                      textvariable=self.controller.shared_data["email"])
        email.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Email")

        passwordL = Label(self, text="Password:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        passwordL.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        password = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show="*")
        password.grid(row=7, column=1, columnspan=3, padx=10, pady=10)
        password.insert(0, "Password")

        refresh()

        forgotPassword = Button(self, text="Forgot your password?", cursor="hand2",
                                command=lambda: controller.show_frame(ForgotPassword), bg="#ca3e47", fg="#FFFFFF",
                                width=20)
        forgotPassword.grid(row=23, column=1, columnspan=3, padx=10, pady=10)

        myButton = Button(self, text="Sign In!", command=login, fg="white", bg="#ca3e47", width=10)
        myButton.grid(row=17, column=1, columnspan=3, padx=10, pady=20)

        buttonStudent = Button(self, text="Student Sign Up", command=backS, bg="#325288", fg="#FFFFFF", width=15)
        buttonStudent.grid(row=21, column=0, columnspan=3, padx=5, pady=5)

        buttonTeacher = Button(self, text="Teacher Sign Up", command=backT, bg="#325288", fg="#FFFFFF", width=15)
        buttonTeacher.grid(row=21, column=2, columnspan=3, padx=5, pady=5)


class StudentRegister(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def register():
            if str(self.name.get()).isspace() or str(self.surname.get()).isspace() or str(email.get()).isspace() or str(
                    password.get()).isspace() or str(passwordA.get()).isspace() or str(self.studentID.get()).isspace():
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(self.name.get())) == 0 or len(str(self.surname.get())) == 0 or len(
                    str(email.get())) == 0 or len(
                str(password.get())) == 0 or len(str(passwordA.get())) == 0 or len(str(self.studentID.get())) == 0:
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif not str(self.name.get()).isalpha() or not str(self.surname.get()).isalpha():
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("Wrong Input", "Your name or surname typed wrong.")
            elif not str(email.get()).endswith("@isik.edu.tr"):
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("Wrong Email", "Please enter your Işık University Email.")
            elif len(str(password.get())) < 6:
                self.studentID.configure(state=DISABLED)
                messagebox.showwarning("Short Password", "Your password is shorter than 6 characters.")
            elif len(str(password.get())) > 16:
                self.studentID.configure(state=DISABLED)
                messagebox.showwarning("Short Password", "Your password is longer than 16 characters.")
            elif str(password.get()) != str(passwordA.get()):
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("Password Mismatch", "Your passwords do not match.")
            elif not len(
                    db.child("students").order_by_child("id").equal_to(
                        (str(self.studentID.get()))[:-1]).get().val()) == 0:
                self.studentID.configure(state=DISABLED)
                messagebox.showerror("ID Already Exists", "This ID is registered to the system.")
            else:
                try:
                    auth1.create_user_with_email_and_password(str(email.get()), str(password.get()))
                except:
                    self.studentID.configure(state=DISABLED)
                    messagebox.showerror("Email Already Exists", "This email is registered to the system.")
                    return
                self.studentID.configure(state=NORMAL)
                encoding = takePhoto()
                registerStudent(str(self.name.get()), str(self.surname.get()), (str(self.studentID.get()))[:-1],
                                str(email.get()),
                                encoding, str(password.get()))
                login = auth1.sign_in_with_email_and_password(str(email.get()), str(password.get()))
                auth1.send_email_verification(login["idToken"])
                messagebox.showinfo("User Created", "Check your email to complete registration.")
                back()

        def registerStudent(name, surname, id, email, encoding, password):
            data1 = {"name": name, "surname": surname, "id": id, "email": email,
                     "encoding": encoding}

            db.child("students").child(id).set(data1)

        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(img, model="hog")
                encode = face_recognition.face_encodings(img, boxes, model="small")[0]
                # print(encode)
                encodeList.append(encode)
            return encodeList

        def takePhoto():
            myList = os.listdir('Temp')
            filtered_files = [file for file in myList if file.endswith(".png")]
            for file in filtered_files:
                path_to_file = os.path.join("Temp", file)
                os.remove(path_to_file)
            font = cv2.FONT_HERSHEY_SIMPLEX
            org = (00, 420)
            org2 = (00, 450)
            fontScale = 0.75
            colorRed = (0, 0, 255)
            colorGreen = (0, 128, 0)
            thickness = 2
            status = False

            cam = cv2.VideoCapture(0)

            while True:
                ret, frame = cam.read()
                if not ret:
                    break
                if (status):
                    cv2.putText(frame, "Facial Encodings are taken", org, font, fontScale,
                                colorGreen, thickness, cv2.LINE_AA, False)
                    cv2.putText(frame, "Press Esc to exit", org2, font, fontScale,
                                colorRed, thickness, cv2.LINE_AA, False)
                else:
                    cv2.putText(frame, "Press Space to take facial encodings", org, font, fontScale,
                                colorRed, thickness, cv2.LINE_AA, False)

                cv2.imshow("FaceNet", frame)

                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed

                    break
                elif k % 256 == 32:
                    # SPACE pressed

                    parent = Path(__file__).parent

                    registerPic = Path(parent, 'Temp', 'TEST.png').__str__()

                    cv2.imwrite(registerPic, frame)
                    myList = os.listdir('Temp')

                    images = []
                    for cl in myList:
                        x = Path(parent, 'Temp')
                        curImg = cv2.imread(f'{x}/{cl}')
                        images.append(curImg)

                    facesCurFrame = face_recognition.face_locations(images[0])

                    if (len(facesCurFrame) == 1):
                        encodelist = findEncodings(images)
                        if (len(encodelist[0]) > 127):
                            status = True
                        else:
                            status = False
                    else:
                        status = False

            cam.release()

            cv2.destroyAllWindows()
            return list(encodelist[0])

        def refresh():
            self.studentID.bind("<FocusIn>", lambda args: self.studentID.delete(0, 'end'))
            email.bind("<FocusIn>", lambda args: email.delete(0, 'end'))
            password.bind("<FocusIn>", lambda args: password.delete(0, 'end'))
            passwordA.bind("<FocusIn>", lambda args: passwordA.delete(0, 'end'))

        def back():
            self.name.delete(0, 'end')
            self.name.insert(0, "Name")
            self.surname.delete(0, 'end')
            self.surname.insert(0, "Surname")
            self.studentID.configure(state=NORMAL)
            self.studentID.delete(0, 'end')
            self.studentID.insert(0, "Student ID")
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            passwordA.delete(0, 'end')
            passwordA.insert(0, "Password")
            controller.show_frame(Login)

        welcome = Label(self, text=" STUDENT SIGN UP ", width=150, height=5, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        self.name = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        self.name.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        self.name.insert(0, "Name")

        self.surname = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        self.surname.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        self.surname.insert(0, "Surname")

        self.studentID = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        self.studentID.grid(row=7, column=1, columnspan=3, padx=10, pady=10)
        self.studentID.insert(0, "Student ID")

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        email.grid(row=9, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Email")

        password = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show='*')
        password.grid(row=11, column=1, columnspan=3, padx=10, pady=10)
        password.insert(0, "Password")

        passwordA = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show='*')
        passwordA.grid(row=13, column=1, columnspan=3, padx=10, pady=10)
        passwordA.insert(0, "Password")

        refresh()

        myButton = Button(self, text="Sign Up!", command=register, fg="white", bg="#ca3e47", width=10)
        myButton.grid(row=15, column=1, columnspan=3, padx=10, pady=10)

        buttonBack = Button(self, text="Back", command=back, bg="#fed049", width=10)
        buttonBack.grid(row=15, column=0, columnspan=3, padx=5, pady=5)

    def cardReader(self):
        name = ""
        surname = ""
        number = ""
        parent = Path(__file__).parent
        # print(parent)
        tessPath = Path(parent, "cardReader", "tesseract.exe").__str__()
        # print(tessPath)
        pytesseract.pytesseract.tesseract_cmd = tessPath
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("test")
        while True:
            ret, frame = cam.read()
            if not ret:
                # print("failed to grab frame")
                break

            font = cv2.FONT_HERSHEY_SIMPLEX
            # org
            org = (350, 470)
            org2 = (00, 430)
            org3 = (00, 450)
            # fontScale
            fontScale = 0.75
            # Red color in BGR
            colorRed = (0, 0, 255)
            colorGreen = (0, 128, 0)
            # Line thickness of 2 px
            thickness = 2
            cv2.rectangle(frame, (5, 5), (635, 400), (255, 0, 0), 2)
            cv2.putText(frame, "ID CARD HERE", (250, 30), font, fontScale, (255, 0, 0), thickness, cv2.LINE_AA)
            cv2.putText(frame, "Name:" + str(name), (350, 430), font, fontScale,
                        colorRed, thickness, cv2.LINE_AA, False)
            cv2.putText(frame, "Surname:" + str(surname), (350, 450), font, fontScale,
                        colorRed, thickness, cv2.LINE_AA, False)
            cv2.putText(frame, "ID:" + str(number[:-1]), org, font, fontScale,
                        colorRed, thickness, cv2.LINE_AA, False)
            cv2.putText(frame, f"Press Space after you align your ID card.", org2, font, 0.5,
                        colorGreen, thickness, cv2.LINE_AA, False)
            cv2.putText(frame, f"Press Esc after checking your information", org3, font, 0.5,
                        colorRed, thickness, cv2.LINE_AA, False)
            cv2.imshow("test", frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                # print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                parent = Path(__file__).parent
                registerPic = Path(parent, 'Temp', 'cardRead.png').__str__()
                cv2.imwrite(registerPic, frame)
                img = cv2.imread(registerPic)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                photo = img[130:280, 210:360]

                text = pytesseract.image_to_string(photo)

                array = text.split(" ")
                # print(array)

                count = 0
                name = ""
                surname = ""
                number = ""

                for word in array:
                    if word.startswith("2") and word[3:5].isalpha() and word[:3].isdigit():
                        # print("Number:")
                        number = word[:10]
                        # print(word[:10])
                    if 3 <= len(word) <= 15 and count == 0:
                        # print("Name:")
                        for i in range(len(word)):
                            if 65 <= ord(word[i]) <= 90:
                                name += word[i]
                        # print(name)
                        count += 1
                    elif 3 <= len(word) <= 15 and count == 1:
                        # print("Surname:")
                        for i in range(len(word)):
                            if 65 <= ord(word[i]) <= 90:
                                surname += word[i]
                        # print(surname)
                        count += 1

        cam.release()

        cv2.destroyAllWindows()

        self.name.delete(0, 'end')
        self.name.insert(0, name)
        self.surname.delete(0, 'end')
        self.surname.insert(0, surname)
        self.studentID.delete(0, 'end')
        self.studentID.insert(0, number)
        self.studentID.configure(state=DISABLED)

    def enable(self):
        self.studentID.configure(state=NORMAL)


class TeacherRegister(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def register():
            if str(name.get()).isspace() or str(surname.get()).isspace() or str(email.get()).isspace() or str(
                    password.get()).isspace() or str(passwordA.get()).isspace():
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(name.get())) == 0 or len(str(surname.get())) == 0 or len(str(email.get())) == 0 \
                    or len(str(password.get())) == 0 or len(str(passwordA.get())) == 0:
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif not str(name.get()).isalpha() or not str(surname.get()).isalpha():
                messagebox.showerror("Wrong Input", "Your name or surname typed wrong.")
            elif not str(email.get()).endswith("@isikun.edu.tr"):
                messagebox.showerror("Wrong Email", "Please enter your Işık University Email.")
            elif len(str(password.get())) < 6:
                messagebox.showwarning("Short Password", "Your password is shorter than 6 characters.")
            elif len(str(password.get())) > 16:
                messagebox.showwarning("Short Password", "Your password is longer than 16 characters.")
            elif str(password.get()) != str(passwordA.get()):
                messagebox.showerror("Password Mismatch", "Your passwords do not match.")
            elif not len(db.child("teachers").order_by_child("email").equal_to(str(email.get())).get().val()) == 0:
                messagebox.showerror("User Already Exists", "This User is registered to the system.")
            else:
                try:
                    auth1.create_user_with_email_and_password(str(email.get()), str(password.get()))
                except:
                    messagebox.showerror("Email Already Exists", "This email is registered to the system.")
                    return
                # print(str(name.get()), str(surname.get()), str(email.get()), str(password.get()))
                registerTeacher(str(name.get()), str(surname.get()), str(email.get()), str(password.get()))
                login = auth1.sign_in_with_email_and_password(str(email.get()), str(password.get()))
                auth1.send_email_verification(login["idToken"])
                messagebox.showinfo("User Created", "Check your email to complete registration.")
                controller.show_frame(Login)

        def registerTeacher(name, surname, email, password):
            data1 = {"name": name, "surname": surname, "email": email}
            croppedEmail = email[:-14]
            croppedEmail = croppedEmail.replace(".", "")
            # print(croppedEmail)
            db.child("teachers").child(croppedEmail).set(data1)

        def refresh():
            name.bind("<FocusIn>", lambda args: name.delete(0, 'end'))
            surname.bind("<FocusIn>", lambda args: surname.delete(0, 'end'))
            email.bind("<FocusIn>", lambda args: email.delete(0, 'end'))
            password.bind("<FocusIn>", lambda args: password.delete(0, 'end'))
            passwordA.bind("<FocusIn>", lambda args: passwordA.delete(0, 'end'))

        def back():
            name.delete(0, 'end')
            name.insert(0, "Name")
            surname.delete(0, 'end')
            surname.insert(0, "Surname")
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            passwordA.delete(0, 'end')
            passwordA.insert(0, "Password")
            controller.show_frame(Login)

        welcome = Label(self, text=" TEACHER SIGN UP ", width=150, height=5, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        name = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        name.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        name.insert(0, "Name")

        surname = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        surname.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        surname.insert(0, "Surname")

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        email.grid(row=9, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Email")

        password = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show="*")
        password.grid(row=11, column=1, columnspan=3, padx=10, pady=10)
        password.insert(0, "Password")

        passwordA = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show="*")
        passwordA.grid(row=13, column=1, columnspan=3, padx=10, pady=10)
        passwordA.insert(0, "Password")

        refresh()

        myButton = Button(self, text="Sign Up!", command=register, fg="white", bg="#ca3e47", width=10)
        myButton.grid(row=15, column=1, columnspan=3, padx=10, pady=10)

        buttonBack = Button(self, text="Back", command=back, bg="#fed049", width=10)
        buttonBack.grid(row=15, column=0, columnspan=3, padx=5, pady=5)


class ForgotPassword(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def mail():
            try:
                auth1.send_password_reset_email(str(email.get()))
                messagebox.showinfo("Email Send", "An email has been send to your email")
            except:
                messagebox.showerror("Unsuccessful Attempt", "Email not found")

        def refresh():
            email.bind("<FocusIn>", lambda args: email.delete(0, 'end'))

        def back():
            email.delete(0, 'end')
            email.insert(0, "Enter your email")
            controller.show_frame(Login)

        welcome = Label(self, text=" FORGOT PASSWORD ", width=150, height=5, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        email.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Enter your email")

        refresh()

        buttonBack = Button(self, text="Back", command=back, bg="#fed049", width=10)
        buttonBack.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        myButton = Button(self, text="Submit", command=mail, fg="white", bg="#ca3e47", width=10)
        myButton.grid(row=5, column=1, columnspan=3, padx=10, pady=10)


class TeacherMainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        image = Image.open("images/FaceNetLogo.png")
        img = ImageTk.PhotoImage(image)

        logoLabel = Label(frameHeader, image=img, borderwidth=0)
        logoLabel.image = img
        logoLabel.pack(side=LEFT)

        logoutButton = Button(frameHeader, text="Logout", command=lambda: controller.show_frame(Login), width=10,
                              bg="#ca3e47", fg="#FFFFFF")
        logoutButton.pack(side=RIGHT)

        global welcomeMessage
        welcomeMessage = tk.StringVar()

        nameLabel = Label(frameHeader, height=6, width=50, bg="#313131", textvariable=welcomeMessage, fg="#FFFFFF")
        welcomeMessage.set("")
        nameLabel.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        frameButtons = Frame(frameCenter, height=700, width=900, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameButtons.pack(side=LEFT)

        buttonCC = Button(frameButtons, text="Create Course", command=lambda: controller.show_frame(CreateCourse),
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonCC.grid(row=0, column=1, columnspan=3, padx=10, pady=40)

        buttonDC = Button(frameButtons, text="Delete Course", command=lambda: controller.show_frame(DeleteCourse),
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonDC.grid(row=2, column=1, columnspan=3, padx=10, pady=40)

        buttonCE = Button(frameButtons, text="Create Exam", command=self.createExam,
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonCE.grid(row=4, column=1, columnspan=3, padx=10, pady=40)

        buttonDE = Button(frameButtons, text="Delete Exam", command=lambda: controller.show_frame(DeleteExam),
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonDE.grid(row=6, column=1, columnspan=3, padx=10, pady=40)

        buttonER = Button(frameButtons, text="Exam Reports", command=self.openExamReportsPage,
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonER.grid(row=8, column=1, columnspan=3, padx=10, pady=40)

        # buttonRefresh = Button(frameButtons, text="Refresh", command=self.courses, width=13, bg="#ca3e47",
        # fg="#FFFFFF")
        # buttonRefresh.grid(row=9, column=1, columnspan=3, padx=10, pady=40)

        frameCE = Frame(frameCenter, height=700, width=1350, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameCE.pack(side=LEFT, fill=X)

        f = ('Times', 20)

        courseList = Label(frameCE, height=2, bg="#313131", text="Courses", fg="#FFFFFF", font=f)
        courseList.pack(side=TOP, fill=X)

        self.frameCourses = Frame(frameCE, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.frameCourses.pack(side=TOP, fill=X)

        global coursesofTeacher
        coursesofTeacher = []

        # canvas = Canvas(frameCourses)
        # scroll = ttk.Scrollbar(frameCourses, orient=HORIZONTAL, command=canvas.xview)
        # scroll.pack(side=BOTTOM, fill=X)
        # canvas.configure(xscrollcommand=scroll.set)
        # canvas.pack(side=LEFT)

    def createExam(self):
        self.controller.get_frame(CreateExam).examIDCon()
        self.controller.show_frame(CreateExam)

    def courses(self):
        global coursesofTeacher
        coursesofTeacher = self.getCourseCodesOfTeacher(self.controller.shared_data["email"].get())
        courses = coursesofTeacher

        # print(courses)

        for widget in self.frameCourses.winfo_children():
            widget.destroy()

        for course in courses:
            self.frameCourse = Frame(self.frameCourses, height=450, width=250, bg="#414141", borderwidth=2,
                                     relief=SUNKEN)
            self.frameCourse.pack(side=LEFT)

            self.labelCourse = Label(self.frameCourse, height=3, width=28, bg="#313131", text=course[1], fg="#FFFFFF")
            self.labelCourse.place(x=25, y=50)

            self.labelCourseAbb = Label(self.frameCourse, height=3, width=28, bg="#313131", text=course[0],
                                        fg="#FFFFFF")
            self.labelCourseAbb.place(x=25, y=150)

            self.buttonDetail = Button(self.frameCourse, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                                       command=lambda courseID=course[0]: self.openCourseDetail(courseID))
            # threading.Thread(target= , args =[]).start()
            self.buttonDetail.place(x=75, y=250)

            self.buttonExams = Button(self.frameCourse, text="Exams", width=13, bg="#ca3e47", fg="#FFFFFF",
                                      command=lambda courseID=course[0]: self.openExamDetail(courseID))
            # threading.Thread(target= , args =[]).start()
            self.buttonExams.place(x=75, y=320)

    def getCourseCodesOfTeacher(self, teacherMail):
        coursesArrays = []

        result = db.child("courses").order_by_child("TeacherMail").equal_to(teacherMail).get()

        for course in result:
            stuListResult = db.child("coursesENROLL").child(course.key()).shallow().get()
            stuList = list(stuListResult.val())
            courseArray = []
            courseArray.append(str(course.key()))
            courseArray.append(course.val()["CourseName"])
            courseArray.append(stuList)
            coursesArrays.append(courseArray)

        # print(coursesArrays)

        return coursesArrays

    def openCourseDetail(self, courseID):
        self.controller.shared_data["selectedCourse"] = courseID
        # print(self.controller.shared_data["selectedCourse"])

        global courseAbb
        courseAbb.set(self.controller.shared_data["selectedCourse"])

        result123 = db.child("courses").child(self.controller.shared_data["selectedCourse"]).get()

        global courseName
        courseName.set(result123.val()["CourseName"])

        self.controller.get_frame(CourseDetailPage).getStudents()

        self.controller.show_frame(CourseDetailPage)

    def openExamDetail(self, courseID):
        self.controller.shared_data["selectedCourse"] = courseID

        global courseAbb
        courseAbb.set(self.controller.shared_data["selectedCourse"])

        result123 = db.child("courses").child(self.controller.shared_data["selectedCourse"]).get()

        global courseName
        courseName.set(result123.val()["CourseName"])

        self.controller.get_frame(TeacherCoursePage).exams()

        self.controller.show_frame(TeacherCoursePage)

    def openExamReportsPage(self):
        self.controller.get_frame(ExamReports).buttons()
        self.controller.show_frame(ExamReports)


class StudentMainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        image = Image.open("images/FaceNetLogo.png")
        img = ImageTk.PhotoImage(image)

        logoLabel = Label(frameHeader, image=img, borderwidth=0)
        logoLabel.image = img
        logoLabel.pack(side=LEFT)

        logoutButton = Button(frameHeader, text="Logout", command=lambda: controller.show_frame(Login), width=10,
                              bg="#ca3e47", fg="#FFFFFF")
        logoutButton.pack(side=RIGHT)

        global welcomeMessageStudent
        welcomeMessageStudent = tk.StringVar()

        nameLabel = Label(frameHeader, height=6, width=50, bg="#313131", textvariable=welcomeMessageStudent,
                          fg="#FFFFFF")
        welcomeMessageStudent.set("")
        nameLabel.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        frameButtons = Frame(frameCenter, height=700, width=900, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameButtons.pack(side=LEFT)

        buttonTF = Button(frameButtons, text="Test FaceRec", command=self.test,
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonTF.grid(row=1, column=1, columnspan=3, padx=10, pady=40)

        buttonTE = Button(frameButtons, text="Test EyeGaze", command=self.capture,
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonTE.grid(row=3, column=1, columnspan=3, padx=10, pady=40)

        buttonCP = Button(frameButtons, text="Change Picture", command=self.change,
                          width=13, bg="#ca3e47", fg="#FFFFFF")
        buttonCP.grid(row=5, column=1, columnspan=3, padx=10, pady=40)

        buttonCC = Button(frameButtons, text="Change Password", command=self.changePass,
                          width=15, bg="#ca3e47", fg="#FFFFFF")
        buttonCC.grid(row=7, column=1, columnspan=3, padx=10, pady=40)

        # buttonRefresh = Button(frameButtons, text="Refresh", command=self.courses, width=13, bg="#ca3e47",
        # fg="#FFFFFF")
        # buttonRefresh.grid(row=9, column=1, columnspan=3, padx=10, pady=40)

        f = ('Times', 20)

        frameCE = Frame(frameCenter, height=700, width=1350, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameCE.pack(side=LEFT, fill=X)

        courseList = Label(frameCE, height=2, bg="#313131", text="Courses", fg="#FFFFFF", font=f)
        courseList.pack(side=TOP, fill=X)

        self.frameCourses = Frame(frameCE, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.frameCourses.pack(side=TOP, fill=X)

        canvas = Canvas(self.frameCourses)
        frameScroll = Frame(canvas)
        xscrollbar = ttk.Scrollbar(self.frameCourses, orient=HORIZONTAL, command=canvas.xview)
        # canvas.configure(canvas.xview_scroll())

        xscrollbar.pack(side=BOTTOM, fill=X)

        # canvas.pack(side=LEFT)

        global coursesofStudent
        coursesofStudent = []

    def coursesS(self):
        global coursesofStudent
        coursesofStudent = self.getCoursesOfStudent(self.getIDfromMail(self.controller.shared_data["email"].get()))

        for widget in self.frameCourses.winfo_children():
            widget.destroy()

        for course in coursesofStudent:
            self.frameCourse = Frame(self.frameCourses, height=450, width=250, bg="#414141", borderwidth=2,
                                     relief=SUNKEN)
            self.frameCourse.pack(side=LEFT)

            self.labelCourse = Label(self.frameCourse, height=3, width=28, bg="#313131", text=course[1], fg="#FFFFFF")
            self.labelCourse.place(x=25, y=50)

            self.labelCourseAbb = Label(self.frameCourse, height=3, width=28, bg="#313131", text=course[0],
                                        fg="#FFFFFF")
            self.labelCourseAbb.place(x=25, y=140)

            self.labelTeacher = Label(self.frameCourse, height=3, width=28, bg="#313131", text=course[2],
                                      fg="#FFFFFF")
            self.labelTeacher.place(x=25, y=230)

            self.buttonCourse = Button(self.frameCourse, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                                       command=lambda courseID=course[0]: self.openCourseDetail(courseID))
            self.buttonCourse.place(x=75, y=330)

    def getCoursesOfStudent(self, studentID):
        coursesArrays = []
        courseQu = db.child("courses").get()

        for a in courseQu:
            temp = []
            temp.append(a.key())
            temp.append(a.val()['CourseName'])
            temp.append(a.val()['TeacherMail'])
            coursesArrays.append(temp)

        studentsCourses = []
        for course in coursesArrays:
            result = db.child("coursesENROLL").child(course[0]).child(studentID).get()
            if result.val() is not None:
                studentsCourses.append(course)

        # print(studentsCourses)
        return studentsCourses

    def getIDfromMail(self, mail):
        result = db.child("students").order_by_child("email").equal_to(mail).get()
        studentID = ""
        # print(result.val())
        if len(result.val()) != 0:
            studentID = list(result.val())[0]
        # print(studentID)
        return studentID

    def getIDfromMailS(self, mail):
        resultIDS = db.child("students").order_by_child("email").equal_to(mail).get()
        studentID = list(resultIDS.val())[0]
        return studentID

    def openCourseDetail(self, courseID):
        self.controller.shared_data["selectedCourse"] = courseID
        # print(self.controller.shared_data["selectedCourse"])

        global courseAbb
        courseAbb.set(self.controller.shared_data["selectedCourse"])

        result123 = db.child("courses").child(self.controller.shared_data["selectedCourse"]).get()

        global courseName
        courseName.set(result123.val()["CourseName"])

        self.controller.get_frame(CoursePageS).examsS()

        self.controller.show_frame(CoursePageS)

    def test(self):
        studentID = self.getIDfromMailS(self.controller.shared_data["email"].get())
        self.faceRecogCheck(studentID)
        self.controller.get_frame(StudentMainPage).coursesS()

    def faceRecogCheck(self, studentID):
        countOfSucces = 0
        result = db.child("students").child(studentID).get()
        faceEncoding = np.asarray(result.val()["encoding"])
        cap = cv2.VideoCapture(0)
        escapecondition = True

        while True:
            k = cv2.waitKey(1)

            if k % 256 == 27:
                # ESC pressed
                escapecondition = False
                # print("Escape hit, closing...")
                break
            success, img = cap.read()
            if not success:
                # print("failed to grab frame")
                break
            if countOfSucces == 5:
                # print("Exit first While")
                break

            font = cv2.FONT_HERSHEY_SIMPLEX
            # org
            org = (00, 420)
            org2 = (00, 450)
            # fontScale
            fontScale = 0.75
            # Red color in BGR
            colorRed = (0, 0, 255)
            colorWhite = (255, 255, 255)
            # Line thickness of 2 px
            thickness = 2
            cv2.putText(img, "Face Recognition still in progress", org, font, fontScale,
                        colorRed, thickness, cv2.LINE_AA, False)
            cv2.putText(img, "Hold Escape to Exit", org2, font, fontScale,
                        colorWhite, thickness, cv2.LINE_AA, False)
            cv2.imshow("test", img)
            imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgSmall)
            # print(len(facesCurFrame))
            # print(facesCurFrame)
            encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)
            # print(encodesCurFrame)
            if (len(encodesCurFrame) == 1):
                matches = face_recognition.compare_faces(faceEncoding, encodesCurFrame, 0.56)
                # print(matches[0])
                if (matches[0]):
                    countOfSucces = countOfSucces + 1

            cv2.waitKey(1)
        if escapecondition == True:
            while True:
                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed
                    escapecondition = False
                    # print("Escape hit, closing...")
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                success, img = cap.read()
                if not success:
                    # print("failed to grab frame")
                    break

                font = cv2.FONT_HERSHEY_SIMPLEX
                # org
                org = (00, 420)
                org2 = (00, 450)
                # fontScale
                fontScale = 0.75
                # Red color in BGR
                colorGreen = (0, 128, 0)
                colorWhite = (255, 255, 255)
                # Line thickness of 2 px
                thickness = 2
                cv2.putText(img, "Face Recognition Completed Successfully", org, font, fontScale,
                            colorGreen, thickness, cv2.LINE_AA, False)
                cv2.putText(img, "Hold Escape to Exit", org2, font, fontScale,
                            colorWhite, thickness, cv2.LINE_AA, False)
                cv2.imshow("test", img)
                cv2.waitKey(1)

    def capture(self):
        gaze = GazeTracking()
        webcam = cv2.VideoCapture(0)

        while True:
            # We get a new frame from the webcam
            _, frame = webcam.read()

            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)

            frame = gaze.annotated_frame()
            text = ""

            if gaze.is_right():
                text = "Looking right"
            elif gaze.is_left():
                text = "Looking left"
            elif gaze.is_center():
                text = "Looking center"
            elif gaze.is_top():
                text = "Looking top"
            elif gaze.is_bottom():
                text = "Looking bottom"

            cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (147, 58, 31), 1)
            cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (147, 58, 31),
                        1)
            cv2.putText(frame, "Press Esc to exit", (10, 450), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                        (0, 128, 0), 2)

            cv2.imshow("Demo", frame)

            if cv2.waitKey(1) == 27:
                webcam.release()
                cv2.destroyAllWindows()
                break

    def change(self):
        studentID = self.getIDfromMailS(self.controller.shared_data["email"].get())
        self.changeEncoding(studentID)
        self.controller.get_frame(StudentMainPage).coursesS()

    def changeEncoding(self, studentID):
        state = False
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("test")
        while True:
            ret, frame = cam.read()
            if not ret:
                # print("failed to grab frame")
                break
            if state:
                font = cv2.FONT_HERSHEY_SIMPLEX
                # org
                org = (00, 420)
                org2 = (00, 450)
                # fontScale
                fontScale = 0.75
                # Red color in BGR
                colorGreen = (0, 128, 0)
                colorWhite = (255, 255, 255)
                # Line thickness of 2 px
                thickness = 2
                cv2.putText(frame, "Face Encoding Taken Succesfully", org, font, fontScale,
                            colorGreen, thickness, cv2.LINE_AA, False)
                cv2.putText(frame, "Hold Escape to exit and finish the update.", org2, font, fontScale,
                            colorWhite, thickness, cv2.LINE_AA, False)
            if state == False:
                font = cv2.FONT_HERSHEY_SIMPLEX
                # org
                org = (00, 420)
                org2 = (00, 450)
                # fontScale
                fontScale = 0.75
                # Red color in BGR
                colorRed = (0, 0, 255)
                colorWhite = (255, 255, 255)
                # Line thickness of 2 px
                thickness = 2
                cv2.putText(frame, "Face Encoding is not taken, Press Space to take picture.", org, font, 0.65,
                            colorRed, thickness, cv2.LINE_AA, False)
                cv2.putText(frame, "Hold Escape to exit.", org2, font, fontScale,
                            colorWhite, thickness, cv2.LINE_AA, False)

            cv2.imshow("test", frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                # print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                parent = Path(__file__).parent
                myList = os.listdir('Temp')
                filtered_files = [file for file in myList if file.endswith(".png")]
                for file in filtered_files:
                    path_to_file = os.path.join("Temp", file)
                    os.remove(path_to_file)
                registerPic = Path(parent, 'Temp', 'TEST.png').__str__()

                cv2.imwrite(registerPic, frame)
                myList = os.listdir('Temp')
                # print(myList)
                images = []
                for cl in myList:
                    x = Path(parent, 'Temp')
                    curImg = cv2.imread(f'{x}/{cl}')
                    images.append(curImg)
                # print(images)
                # print(len(images[0]))
                try:
                    encodelist = self.findEncodings(images)
                    # print(len(encodelist))
                    if len(encodelist[0]) > 125:
                        # print("image is okay")
                        state = True
                    else:
                        pass
                        # print("it is not okay")
                except:
                    state = False
        if state:
            db.child("students").child(studentID).update({"encoding": list(encodelist[0])})

        cam.release()
        cv2.destroyAllWindows()

    def findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img, model="hog")
            encode = face_recognition.face_encodings(img, boxes, model="small")[0]
            # print(encode)
            encodeList.append(encode)
        return encodeList

    def changePass(self):
        if messagebox.askyesno("Confirm Changing Password?", "Are you sure you want to change your password?"):
            try:
                auth1.send_password_reset_email(self.controller.shared_data["email"].get())
                messagebox.showinfo("Email Sent", "An email has been send to your email")
            except:
                messagebox.showerror("Email Didn't Send", "Something wrong with the system!")
        else:
            return True

        self.controller.get_frame(StudentMainPage).coursesS()


# TEACHER PAGES


class CreateCourse(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def back():
            self.documentLabel.configure(text="File Name")
            courseNameE.delete(0, 'end')
            courseNameE.insert(0, "Course Name")
            courseAbbE.delete(0, 'end')
            courseAbbE.insert(0, "Course Abbreviation")
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        def refresh():
            courseNameE.bind("<FocusIn>", lambda args: courseNameE.delete(0, 'end'))
            courseAbbE.bind("<FocusIn>", lambda args: courseAbbE.delete(0, 'end'))

        def create():
            courseQu = db.child("courses").shallow().get()
            courseCodesArray = []
            if courseQu.val() is not None:
                courseCodesArray = list(courseQu.val())

            if str(courseNameE.get()).isspace() or str(courseAbbE.get()).isspace():
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(courseNameE.get())) == 0 or len(str(courseAbbE.get())) == 0:
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(courseAbbE.get())) != 8 or not str(courseAbbE.get())[:4].isalpha() or not str(
                    courseAbbE.get())[4:].isdigit():
                messagebox.showerror("Wrong Abbreviation", "Please, check course abbreviation.")
            elif self.documentLabel.cget("text") == "File Name":
                messagebox.showerror("Empty File", "Please, add a csv file")
            elif str(courseAbbE.get()) in courseCodesArray:
                messagebox.showerror("Course Exists", "Please, check your course.")
            else:
                self.createCourses(str(courseNameE.get()), str(courseAbbE.get()),
                                   self.controller.shared_data["email"].get())
                messagebox.showinfo("Course Added", "The course added.")
                self.documentLabel.configure(text="File Name")
                courseNameE.delete(0, 'end')
                courseNameE.insert(0, "Course Name")
                courseAbbE.delete(0, 'end')
                courseAbbE.insert(0, "Course Abbreviation")
                controller.get_frame(TeacherMainPage).courses()
                controller.show_frame(TeacherMainPage)

        welcome = Label(self, text=" ADD COURSE ", width=150, height=10, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        courseNameE = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        courseNameE.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        courseNameE.insert(0, "Course Name")

        courseAbbE = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        courseAbbE.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        courseAbbE.insert(0, "Course Abbreviation")

        refresh()

        backButton = Button(self, text="Back", command=back,
                            width=10, bg="#fed049")
        backButton.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        browseButton = Button(self, text="Browse a File", command=self.fileDialog,
                              width=10, bg="#ca3e47", fg="#FFFFFF")
        browseButton.grid(row=7, column=1, columnspan=3, padx=10, pady=30)

        self.documentLabel = Label(self, text="File Name", width=30)
        self.documentLabel.grid(row=7, column=2, columnspan=3, padx=10, pady=10)

        buttonSubmit = Button(self, text="Submit Class", width=13, bg="#ca3e47", fg="#FFFFFF", command=create)
        buttonSubmit.grid(row=9, column=1, columnspan=3, padx=10, pady=10)

    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetype=
        (("csv files", "*.csv"), ("all files", "*.*")))

        if len(self.filename) == 0:
            messagebox.showwarning("Empty File", "Please add a csv file.")
            self.documentLabel.configure(text="File Name")

        elif not str(self.filename).endswith(".csv"):
            messagebox.showerror("Wrong Type", "Check your file type.")
            self.documentLabel.configure(text="File Name")

        else:
            self.documentLabel.configure(text=self.filename)

    def createCourses(self, courseName, courseID, TeacherMail):
        courseQu = db.child("courses").shallow().get()
        if courseQu.val() is None and not str(self.documentLabel.cget("text")).endswith(".csv"):
            raw_data = pd.read_csv(self.documentLabel.cget("text"))
            # print(raw_data.head(15))
            asarray = np.asarray(raw_data["StudentID"])

            courseData = {"CourseName": courseName, "TeacherMail": TeacherMail}
            db.child("courses").child(courseID).set(courseData)
            enrollData = {"takesCourse": True}
            for student in asarray:
                db.child("coursesENROLL").child(courseID).child(student).set(enrollData)
        else:
            courseCodesArray = []
            if courseQu.val() is not None:
                courseCodesArray = list(courseQu.val())
                # print(courseCodesArray)

            if courseID not in courseCodesArray:
                raw_data = pd.read_csv(self.documentLabel.cget("text"))
                # print(raw_data.head(15))
                asarray = np.asarray(raw_data["StudentID"])

                courseData = {"CourseName": courseName, "TeacherMail": TeacherMail}
                db.child("courses").child(courseID).set(courseData)
                enrollData = {"takesCourse": True}
                for student in asarray:
                    db.child("coursesENROLL").child(courseID).child(student).set(enrollData)
            else:
                messagebox.showerror("Course Exists", "Please, check your course.")
                # print("Course exists")


class DeleteCourse(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def back():
            self.courseAbbC.set("")
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        def delete():
            selected_course = self.courseAbbC.get()
            deleteCourse(selected_course)

        def deleteCourse(courseID):
            courseQu = db.child("courses").shallow().get()
            courseCodesArray = list(courseQu.val())
            # print(courseCodesArray)

            if messagebox.askyesno("Confirm Deletion?", "Are you sure you want to delete this course?"):
                try:
                    self.deleteCourseAllDetails(courseID)
                    db.child("courses").child(courseID).remove()
                    db.child("coursesENROLL").child(courseID).remove()
                    self.courseAbbC.set("")
                    messagebox.showinfo("Course Deleted", "Selected course deleted")
                except:
                    messagebox.showerror("Execution Error", "Something wrong with the system!")
            else:
                return True
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        welcome = Label(self, text=" DELETE COURSE ", width=150, height=10, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        courseL = Label(self, text="Select Course:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        courseL.grid(row=5, column=0, columnspan=3, padx=10, pady=20)

        courses = []

        self.courseAbbC = ttk.Combobox(self, values=courses, state='readonly', width=30, postcommand=self.addCourses)
        self.courseAbbC.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

        backButton = Button(self, text="Back", command=back,
                            width=10, bg="#fed049")
        backButton.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        buttonSubmit = Button(self, text="Delete", width=13, bg="#ca3e47", fg="#FFFFFF", command=delete)
        buttonSubmit.grid(row=9, column=1, columnspan=3, padx=10, pady=10)

    def addCourses(self):
        result = db.child("courses").order_by_child("TeacherMail").equal_to(
            self.controller.shared_data["email"].get()).get()
        result1 = list(result.val())
        # print(result1)

        self.courseAbbC['values'] = result1

    def deleteCourseAllDetails(self, courseID):
        result = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
        for exam in result:
            # print(exam.key())
            self.controller.get_frame(DeleteExam).deleteExamDataOfAllStudents(exam.key())


class CreateExam(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def back():
            refresh()
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        def refresh():
            self.courseAbbC.set("")
            self.examID.set("")

            # hour_dur.delete(0, "end")
            # hour_dur.insert(0, 0)
            # min_dur.delete(0, "end")
            # min_dur.insert(0, 0)

            # min_sb.delete(0, "end")
            # min_sb.insert(0, hour_string)
            # sec_hour.delete(0, "end")
            # sec_hour.insert(0, min_string)

            # attemptNum.delete(0, "end")
            # attemptNum.insert(0, 1)

        def create_Exam():
            if len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + "0" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()),
                           str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + min_dur.get()),
                           str(min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 1 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str("0" + hour_dur.get() + ":" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))

            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + "0" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()),
                           str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 1:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + min_dur.get()),
                           str(min_sb.get() + ":" + "0" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 1 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + min_dur.get()),
                           str("0" + min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 1 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + "0" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))
            elif len(str(hour_dur.get())) == 2 and len(str(min_dur.get())) == 2 and len(str(min_sb.get())) == 2 and len(
                    str(sec_hour.get())) == 2:
                createExam(str(self.courseAbbC.get()), str(hour_dur.get() + ":" + min_dur.get()),
                           str(min_sb.get() + ":" + sec_hour.get()), str(attemptNum.get()),
                           str(self.examID.get()), str(startDate.get_date()))

        def createExam(courseID, duration, startTime, attempt, examType, startDates):
            dateN = startDates.split("/")
            year = int("20" + dateN[2])
            month = int(dateN[0])
            day = int(dateN[1])

            todayE = date.today()
            nowE = datetime.now()

            examQu = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
            if len(self.courseAbbC.get()) == 0 or len(self.examID.get()) == 0:
                messagebox.showwarning("Empty Place", "Fill every part")
            elif str(hour_dur.get()) == "0" and (str(min_dur.get()) == "0" or str(min_dur.get()) == "00"):
                messagebox.showwarning("Duration 0", "Set the duration")
            elif str(min_sb.get()) == "0" and (str(sec_hour.get()) == "0" or str(sec_hour.get()) == "00"):
                messagebox.showwarning("Time 0", "Set the Time")
            else:
                if 0 <= int(min_dur.get()) <= 59 and 0 <= int(sec_hour.get()) <= 59:
                    if year > todayE.year:
                        if len(list(examQu.val())) == 0:
                            examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                        "AttemptNumbers": attempt, "ExamType": examType,
                                        "StartDate": startDates}
                            db.child("exams").child(courseID + "-1").set(examData)
                            messagebox.showinfo("Exam Added", "Created Exam has been added")
                        else:
                            ExamCodesArray = list(examQu.val())
                            # print(ExamCodesArray)
                            result = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
                            numOfExam = "-" + str(1 + int((list(result.val().items()))[-1][0].split("-")[1]))
                            examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                        "AttemptNumbers": attempt, "ExamType": examType,
                                        "StartDate": startDates}
                            db.child("exams").child(courseID + numOfExam).set(examData)
                            messagebox.showinfo("Exam Added", "Created Exam has been added")
                        refresh()
                        controller.get_frame(TeacherMainPage).courses()
                        controller.show_frame(TeacherMainPage)
                    elif year == todayE.year:
                        if day > todayE.month:
                            if len(list(examQu.val())) == 0:
                                examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                            "AttemptNumbers": attempt, "ExamType": examType,
                                            "StartDate": startDates}
                                db.child("exams").child(courseID + "-1").set(examData)
                                messagebox.showinfo("Exam Added", "Created Exam has been added")
                            else:
                                ExamCodesArray = list(examQu.val())
                                # print(ExamCodesArray)
                                result = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
                                numOfExam = "-" + str(1 + int((list(result.val().items()))[-1][0].split("-")[1]))
                                examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                            "AttemptNumbers": attempt, "ExamType": examType,
                                            "StartDate": startDates}
                                db.child("exams").child(courseID + numOfExam).set(examData)
                                messagebox.showinfo("Exam Added", "Created Exam has been added")
                            refresh()
                            controller.get_frame(TeacherMainPage).courses()
                            controller.show_frame(TeacherMainPage)
                        elif day == todayE.month:
                            if month > todayE.day:
                                if len(list(examQu.val())) == 0:
                                    examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                                "AttemptNumbers": attempt, "ExamType": examType,
                                                "StartDate": startDates}
                                    db.child("exams").child(courseID + "-1").set(examData)
                                    messagebox.showinfo("Exam Added", "Created Exam has been added")
                                else:
                                    ExamCodesArray = list(examQu.val())
                                    # print(ExamCodesArray)
                                    result = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
                                    numOfExam = "-" + str(1 + int((list(result.val().items()))[-1][0].split("-")[1]))
                                    examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                                "AttemptNumbers": attempt, "ExamType": examType,
                                                "StartDate": startDates}
                                    db.child("exams").child(courseID + numOfExam).set(examData)
                                    messagebox.showinfo("Exam Added", "Created Exam has been added")
                                refresh()
                                controller.get_frame(TeacherMainPage).courses()
                                controller.show_frame(TeacherMainPage)
                            elif month == todayE.day:
                                if int(min_sb.get()) > nowE.hour:
                                    if len(list(examQu.val())) == 0:
                                        examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                                    "AttemptNumbers": attempt, "ExamType": examType,
                                                    "StartDate": startDates}
                                        db.child("exams").child(courseID + "-1").set(examData)
                                        messagebox.showinfo("Exam Added", "Created Exam has been added")
                                    else:
                                        ExamCodesArray = list(examQu.val())
                                        # print(ExamCodesArray)
                                        result = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
                                        numOfExam = "-" + str(
                                            1 + int((list(result.val().items()))[-1][0].split("-")[1]))
                                        examData = {"CourseID": courseID, "Duration": duration, "StartTime": startTime,
                                                    "AttemptNumbers": attempt, "ExamType": examType,
                                                    "StartDate": startDates}
                                        db.child("exams").child(courseID + numOfExam).set(examData)
                                        messagebox.showinfo("Exam Added", "Created Exam has been added")
                                    refresh()
                                    controller.get_frame(TeacherMainPage).courses()
                                    controller.show_frame(TeacherMainPage)
                                elif int(min_sb.get()) == nowE.hour:
                                    if int(sec_hour.get()) > nowE.minute:
                                        if len(list(examQu.val())) == 0:
                                            examData = {"CourseID": courseID, "Duration": duration,
                                                        "StartTime": startTime,
                                                        "AttemptNumbers": attempt, "ExamType": examType,
                                                        "StartDate": startDates}
                                            db.child("exams").child(courseID + "-1").set(examData)
                                            messagebox.showinfo("Exam Added", "Created Exam has been added")
                                        else:
                                            ExamCodesArray = list(examQu.val())
                                            # print(ExamCodesArray)
                                            result = db.child("exams").order_by_child("CourseID").equal_to(
                                                courseID).get()
                                            numOfExam = "-" + str(
                                                1 + int((list(result.val().items()))[-1][0].split("-")[1]))
                                            examData = {"CourseID": courseID, "Duration": duration,
                                                        "StartTime": startTime,
                                                        "AttemptNumbers": attempt, "ExamType": examType,
                                                        "StartDate": startDates}
                                            db.child("exams").child(courseID + numOfExam).set(examData)
                                            messagebox.showinfo("Exam Added", "Created Exam has been added")
                                        refresh()
                                        controller.get_frame(TeacherMainPage).courses()
                                        controller.show_frame(TeacherMainPage)
                                    else:
                                        messagebox.showerror("Time Passed", "Minutes passed")
                                else:
                                    messagebox.showerror("Time Passed", "Hour passed")
                            else:
                                messagebox.showwarning("Date Passed", "Select available date")
                        else:
                            messagebox.showwarning("Date Passed", "Select available date")
                    else:
                        messagebox.showwarning("Date Passed", "Select available date")
                else:
                    messagebox.showerror("Time Error", "Check the minutes")

        mainFrame = Frame(self, height=600, width=1050, bg="#414141", padx=20, relief=SUNKEN)
        mainFrame.pack(side=TOP)

        welcome = Label(mainFrame, text=" CREATE EXAM ", width=150, height=10, bg="#414141", fg="#FFFFFF")
        welcome.pack(side=TOP)

        leftL = Frame(mainFrame, height=350, width=200, bg="#414141", relief=SUNKEN)
        leftL.pack(side=LEFT)

        firstL = Frame(leftL, height=100, width=100, bg="#414141")
        firstL.pack(fill=BOTH)

        courseL = Label(firstL, text="Select Course:", width=12, height=2, bg="#313131", fg="#FFFFFF")
        courseL.pack(pady=10, side=LEFT, expand=True)

        courses = []

        self.courseAbbC = ttk.Combobox(firstL, values=courses, state='readonly', width=20, postcommand=self.getCourses)
        self.courseAbbC.pack(pady=10, side=LEFT)

        secondL = Frame(leftL, height=100, width=100, bg="#414141")
        secondL.pack(fill=BOTH)

        examL = Label(secondL, text="Select Exam Type:", width=15, height=2, bg="#313131", fg="#FFFFFF")
        examL.pack(pady=10, side=LEFT, expand=True)

        self.examID = ttk.Combobox(secondL, state='readonly', width=20, postcommand=self.examIDCon)
        self.examID.pack(pady=10, side=LEFT)

        rightL = Frame(mainFrame, height=450, width=200, bg="#414141", relief=SUNKEN)
        rightL.pack(side=RIGHT)

        firstR = Frame(rightL, height=300, width=300, bg="#414141")
        firstR.pack(fill=BOTH)

        dateL = Label(firstR, text="Select Exam Date:", width=15, height=2, bg="#313131", fg="#FFFFFF")
        dateL.pack(pady=10, side=LEFT, expand=True)

        today = date.today()
        now = datetime.now()

        startDate = Calendar(firstR, selectmode='day', year=today.year, month=today.month, day=today.day,
                             date_pattern='dd/mm/yy')
        startDate.pack(side=LEFT)

        hour_string = StringVar()
        min_string = StringVar()
        hour_d_string = StringVar()
        min_d_string = StringVar()
        f = ('Times', 20)

        secondR = Frame(rightL, height=200, width=100, bg="#414141")
        secondR.pack(fill=BOTH)

        timeL = Label(secondR, text="Select Exam Time:", width=15, height=2, bg="#313131", fg="#FFFFFF")
        timeL.pack(pady=10, side=LEFT, expand=True)

        min_sb = Spinbox(secondR, from_=8, to=23, wrap=True, textvariable=hour_string, width=2, state="readonly",
                         font=f, justify=CENTER)
        sec_hour = Spinbox(secondR, from_=0, to=59, wrap=True, textvariable=min_string, font=f, width=2, justify=CENTER)
        hour_string.set(int(now.hour))
        min_string.set(int(now.minute))
        min_sb.pack(side=LEFT, fill=X, expand=True)
        sec_hour.pack(side=LEFT, fill=X, expand=True)

        thirdL = Frame(leftL, height=200, width=100, bg="#414141")
        thirdL.pack(fill=BOTH)

        durL = Label(thirdL, text="Select Duration (Hour/Minute):", width=25, height=2, bg="#313131", fg="#FFFFFF")
        durL.pack(pady=10, side=LEFT, expand=True)

        hour_dur = Spinbox(thirdL, from_=0, to=9, wrap=True, textvariable=hour_d_string, width=2, state="readonly",
                           font=f, justify=CENTER)
        min_dur = Spinbox(thirdL, from_=0, to=59, wrap=True, textvariable=min_d_string, font=f, width=2, justify=CENTER)

        hour_dur.pack(side=LEFT, fill=X, expand=True)
        min_dur.pack(side=LEFT, fill=X, expand=True)

        forthL = Frame(leftL, height=200, width=100, bg="#414141")
        forthL.pack(fill=BOTH)

        ateL = Label(forthL, text="Select Attempt Number:", width=20, height=2, bg="#313131", fg="#FFFFFF")
        ateL.pack(pady=10, side=LEFT, expand=True)

        attemptNum = Spinbox(forthL, from_=1, to=10, wrap=True, width=2, state="readonly", font=f, justify=CENTER)
        attemptNum.pack(pady=10)

        backButton = Button(self, text="Back", command=back,
                            width=10, bg="#fed049")
        backButton.pack(pady=10)

        buttonSubmit = Button(self, text="Create", width=13, bg="#ca3e47", fg="#FFFFFF", command=create_Exam)
        buttonSubmit.pack(pady=10)

    def getCourses(self):
        result = db.child("courses").order_by_child("TeacherMail").equal_to(
            self.controller.shared_data["email"].get()).get()
        result1 = list(result.val())
        # print(result1)

        self.courseAbbC['values'] = result1

    def filterExamType(self, courseID):
        candidateList = ["Midterm 1", "Midterm 2", "Midterm 3", "Final", "Quiz 1", "Quiz 2", "Quiz 3", "Quiz 4",
                         "Quiz 5"]
        result12 = db.child("exams").order_by_child("CourseID").equal_to(courseID).get()
        if len(list(result12.val())) != 0:
            exTypeList = list(result12.val().values())
            currList = []
            for a in exTypeList:
                currList.append(a['ExamType'])

            a = set(candidateList)
            b = set(currList)
            c = {element for element in a if element not in b}
            Z = [x for _, x in sorted(zip(a, c))]
            return Z
        else:
            return candidateList

    def examIDCon(self):
        valuesofType = self.filterExamType(str(self.courseAbbC.get()))
        valuesofType.sort()
        self.examID['values'] = valuesofType


class DeleteExam(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def back():
            self.courseAbbC.set("")
            self.examAbbC.set("")
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        def delete():
            selected_exam = self.examAbbC.get()
            deleteExam(selected_exam)

        def deleteExam(examID):
            abbExam = examID.split("/")[0]
            if not (str(self.examAbbC.get()).isspace() or len(str(self.examAbbC.get())) == 0 or str(
                    self.examAbbC.get()) == ""):
                if messagebox.askyesno("Confirm Deletion?", "Are you sure you want to delete this exam?"):
                    try:
                        self.deleteExamDataOfAllStudents(abbExam)
                        db.child("exams").child(abbExam).remove()
                        self.courseAbbC.set("")
                        self.examAbbC.set("")
                        messagebox.showinfo("Exam Deleted", "Exam deleted")
                    except:
                        messagebox.showerror("Execution Error", "Something wrong with the system!")
                else:
                    return True
                controller.get_frame(TeacherMainPage).courses()
                controller.show_frame(TeacherMainPage)
            else:
                messagebox.showerror("Blank Spaces", "Select exam")

        welcome = Label(self, text=" DELETE EXAM ", width=150, height=10, bg="#414141", fg="#FFFFFF")
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        courseL = Label(self, text="Select Course:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        courseL.grid(row=5, column=0, columnspan=3, padx=10, pady=20)

        courses = []
        exams = []

        self.courseAbbC = ttk.Combobox(self, values=courses, state='readonly', width=30, postcommand=self.addCourses)
        self.courseAbbC.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

        examL = Label(self, text="Select Exam:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        examL.grid(row=7, column=0, columnspan=3, padx=10, pady=20)

        self.examAbbC = ttk.Combobox(self, values=exams, state='readonly', width=30, postcommand=self.addExams)
        self.examAbbC.grid(row=7, column=1, columnspan=3, padx=10, pady=10)

        backButton = Button(self, text="Back", command=back,
                            width=10, bg="#fed049")
        backButton.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

        buttonSubmit = Button(self, text="Delete", width=13, bg="#ca3e47", fg="#FFFFFF", command=delete)
        buttonSubmit.grid(row=11, column=1, columnspan=3, padx=10, pady=10)

    def addCourses(self):
        result = db.child("courses").order_by_child("TeacherMail").equal_to(
            self.controller.shared_data["email"].get()).get()
        result1 = list(result.val())
        # print(result1)

        self.courseAbbC['values'] = result1

    def addExams(self):
        examsResult = db.child("exams").order_by_child("CourseID").equal_to(str(self.courseAbbC.get())).get()
        tempList = []
        for a in examsResult:
            # print(a.key())
            # print(a.val())
            name = str(a.key()) + "/" + str(a.val()["ExamType"])
            tempList.append(name)

        self.examAbbC['values'] = tempList

    def deleteExamDataOfStudent(self, examID, studentID):
        bucket = admin_storage.bucket()
        result = db.child("examEnroll").child(examID).child(studentID).get()
        # print(result.val())
        for a in result:
            # part for attempts
            if a.key() == "Attempts":
                # print(a.val())
                # print(a.val()["Attempt-1"])
                for b in a.val():
                    # print(b)
                    # print(a.val()[b]["PathToImg"])
                    blob = bucket.blob(a.val()[b]["PathToImg"])
                    blob.delete()
            # part for FrChecks
            elif a.key() == "FrChecks":
                # print(a.val())

                for b in a.val():
                    # print(b)
                    # print(a.val()[b]["PathToImg"])
                    if (a.val()[b]["PathToImg"] != ""):
                        blob = bucket.blob(a.val()[b]["PathToImg"])
                        blob.delete()
            # part for Solditute
            elif a.key() == "Solditute":
                # print(a.val())
                # print(a.val()["Attempt-1"])
                for b in a.val():
                    # print(b)
                    # print(a.val()[b]["PathToImg"])
                    blob = bucket.blob(a.val()[b]["PathToImg"])
                    blob.delete()
            elif a.key() == "VidRec":
                # print(a.val())
                # print(a.val()["Attempt-1"])
                for b in a.val():
                    # print(b)
                    # print(a.val()[b]["PathToImg"])
                    blob = bucket.blob(a.val()[b]["PathToVid"])
                    blob.delete()

    def deleteExamDataOfAllStudents(self, examID):
        result = db.child("examEnroll").child(examID).get()

        for student in result:
            # print(student.key())
            self.deleteExamDataOfStudent(examID, student.key())
        db.child("examEnroll").child(examID).remove()


class CourseDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        # logo = ImageTk.PhotoImage(Image.open(""))
        # logoLabel = Label(frameHeader, image=logo)
        # logoLabel.pack(side=LEFT)

        def deleteStudent():
            if messagebox.askyesno("Confirm Deletion?", "Are you sure you want to delete this student?"):
                try:
                    a = getrow()
                    deleteOneStu(self.controller.shared_data["selectedCourse"], a)
                    self.trv.delete(*self.trv.get_children())
                    self.controller.get_frame(CourseDetailPage).getStudents()
                    messagebox.showinfo("Student Deleted", "Student Deleted")
                except:
                    messagebox.showerror("Empty Student", "Student not Selected")
            else:
                return True

        def deleteOneStu(courseID, studentID):
            result = db.child("coursesENROLL").child(courseID).shallow().get()

            # studentList which can be chosen from.
            studentlist = (list(result.val()))

            db.child("coursesENROLL").child(courseID).child(studentID).remove()

        def getrow():
            # rowid = trv.identify_row(event.y)
            item = self.trv.item(self.trv.focus())
            t1.set(item['values'][0])
            # t2.set(item['values'][1])
            # t3.set(item['values'][2])
            return t1.get()

        def toggleCheck(event):
            rowid = self.trv.identify_row(event.y)
            tag = self.trv.item(rowid, "tags")[0]
            tags = list(self.trv.item(rowid, "tags"))
            tags.remove(tag)
            self.trv.item(rowid, tags=tags)
            if tag == "checked":
                self.trv.item(rowid, tags="unchecked")
            else:
                self.trv.item(rowid, tags="checked")

        def toggle2(event):
            for k in self.trv.get_children():
                self.trv.item(k, tags="unchecked")
            toggleCheck(event)

        def addOne():
            result = db.child("coursesENROLL").child(self.controller.shared_data["selectedCourse"]).shallow().get()

            studentlist = (list(result.val()))

            if str(studentID.get()).isspace() or len(str(studentID.get())) == 0:
                messagebox.showerror("Empty ID", "Please enter an student ID")
            elif str(studentID.get()) in studentlist:
                messagebox.showerror("Student Exists", "Student Exists")
            elif len(str(studentID.get())) == 9 or len(str(studentID.get())) == 10:
                addOneStu(self.controller.shared_data["selectedCourse"], studentID.get())
                messagebox.showinfo("Student Added", "Student Added")
                self.trv.delete(*self.trv.get_children())
                self.controller.get_frame(CourseDetailPage).getStudents()
                studentID.delete(0, 'end')
            else:
                messagebox.showerror("Wrong ID", "Entered a wrong ID")

        def addOneStu(courseID, stuID):
            result = db.child("coursesENROLL").child(courseID).shallow().get()
            # studentList which can be chosen from.
            studentlist = (list(result.val()))

            if stuID not in studentlist:
                stuendata = {"takesCourse": True}
                db.child("coursesENROLL").child(courseID).child(stuID).set(stuendata)

        def back():
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)
            self.trv.delete(*self.trv.get_children())

        t1 = StringVar()
        t2 = StringVar()
        t3 = StringVar()

        global courseAbb
        courseAbb = tk.StringVar()

        global courseName
        courseName = tk.StringVar()

        self.courseAbbLabel = Label(frameHeader, height=8, width=20, bg="#313131", textvariable=courseAbb, fg="#FFFFFF")
        self.courseAbbLabel.pack(side=LEFT)

        courseNameLabel = Label(frameHeader, height=8, width=40, bg="#313131", textvariable=courseName, fg="#FFFFFF")
        courseNameLabel.pack(side=LEFT)

        backButton = Button(frameHeader, text="Back", command=back, width=10,
                            bg="#fed049")
        backButton.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        frameLeft = Frame(frameCenter, height=470, width=625, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameLeft.pack(side=LEFT)

        studentListL = Label(frameLeft, width=90, height=2, bg="#313131", text="Student List", fg="#FFFFFF")
        # studentListL.place(x=0, y=0)
        studentListL.pack(side=TOP)

        self.trv = ttk.Treeview(frameLeft, columns=(1, 2, 3), height=10)
        style = ttk.Style(self.trv)
        style.configure('Treeview', rowheight=30)

        self.trv.tag_configure('checked')
        self.trv.tag_configure('unchecked')

        self.trv.heading('#0', text="")
        self.trv.column("#0", minwidth=0, width=50)
        self.trv.heading('#1', text="Student ID")
        self.trv.column("#1", minwidth=0, width=100)
        self.trv.heading('#2', text="Name / Surname")
        self.trv.column("#2", minwidth=0, width=220)
        self.trv.heading('#3', text="Student Email")
        self.trv.column("#3", minwidth=0, width=250)

        # self.trv.bind('<Button 1>', toggle2)

        yscrollbar = ttk.Scrollbar(frameLeft, orient="vertical", command=self.trv.yview)

        global studentIDList
        studentIDList = []

        global studentNameList
        studentNameList = []

        global studentEmailList
        studentEmailList = []

        self.getStudents()

        # self.trv.place(x=0, y=50)
        self.trv.pack(side=LEFT)

        # yscrollbar.place(x=605, y=75)
        yscrollbar.pack(side="right", fill="y")

        self.trv.configure(yscrollcommand=yscrollbar.set)

        frameRight = Frame(frameCenter, height=470, width=425, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameRight.pack(side=LEFT, fill=X)

        studentAddL = Label(frameRight, text="Add Student", width=10, height=2, bg="#313131", fg="#FFFFFF")
        studentAddL.place(x=170, y=30)

        studentIDL = Label(frameRight, text="Student ID:", width=10, height=2, bg="#313131", fg="#FFFFFF")
        studentIDL.place(x=25, y=96)

        studentID = Entry(frameRight, width=30, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        studentID.place(x=120, y=100)

        buttonAddS = Button(frameRight, text="Add", width=13, bg="#ca3e47", fg="#FFFFFF", command=addOne)
        buttonAddS.place(x=160, y=160)

        studentAddL = Label(frameRight, text="Remove Selected Student", width=20, height=2, bg="#313131", fg="#FFFFFF")
        studentAddL.place(x=140, y=280)

        buttonDelS = Button(frameRight, text="Delete", width=13, bg="#ca3e47", fg="#FFFFFF", command=deleteStudent)
        buttonDelS.place(x=160, y=370)

    def getStudents(self):
        global studentIDList
        studentIDList.clear()
        global studentNameList
        studentNameList.clear()
        global studentEmailList
        studentEmailList.clear()

        studentIDList = self.getCourseDetails(self.controller.shared_data["selectedCourse"])[0]
        studentNameList = self.getCourseDetails(self.controller.shared_data["selectedCourse"])[1]
        studentEmailList = self.getCourseDetails(self.controller.shared_data["selectedCourse"])[2]
        i = 0
        # print(studentList)
        for studentID, studentName, studentEmail in zip(studentIDList, studentNameList, studentEmailList):
            self.trv.insert(parent='', index='end', iid=i, text="", values=(studentID, studentName, studentEmail))
            i += 1

    def getCourseDetails(self, courseID):
        stuListResult = db.child("coursesENROLL").child(courseID).shallow().get()

        if stuListResult.val() is None:
            return [[], [], []]
        else:
            stuList = list(stuListResult.val())
            # print(stuList)
            resultlist = []
            idlist = []
            namelist = []
            maillist = []
            for student in stuList:
                stuDetRes = db.child("students").child(student).get()
                # print(stuDetRes.val())
                if stuDetRes.val() == None:
                    idlist.append(student)
                    namelist.append("-")
                    maillist.append("-")
                else:
                    idlist.append(stuDetRes.val()['id'])
                    namelist.append(str(stuDetRes.val()['name'] + " " + stuDetRes.val()['surname']))
                    maillist.append(stuDetRes.val()['email'])

            resultlist.append(idlist)
            resultlist.append(namelist)
            resultlist.append(maillist)
            # print(resultlist)
            return resultlist


class ExamDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        def back():
            controller.get_frame(TeacherCoursePage).exams()
            controller.show_frame(TeacherCoursePage)

        global examAbb
        examAbb = tk.StringVar()

        global examType
        examType = tk.StringVar()

        global examDate
        examDate = tk.StringVar()

        global examTime
        examTime = tk.StringVar()

        global examDuration
        examDuration = tk.StringVar()

        global examAttempt
        examAttempt = tk.StringVar()

        self.examAbbLabel = Label(frameHeader, height=8, width=20, bg="#313131", textvariable=examAbb, fg="#FFFFFF")
        self.examAbbLabel.pack(side=LEFT)

        examTypeLabel = Label(frameHeader, height=8, width=40, bg="#313131", textvariable=examType, fg="#FFFFFF")
        examTypeLabel.pack(side=LEFT)

        backButton = Button(frameHeader, text="Back", command=back, width=10,
                            bg="#fed049")
        backButton.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        frameLeft = Frame(frameCenter, height=470, width=325, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameLeft.pack(side=LEFT)

        examDateLOld = Label(frameLeft, width=20, height=2, bg="#313131", text="Exam Date:", fg="#FFFFFF")
        examDateLOld.place(x=40, y=50)

        labelExamName = Label(frameLeft, height=2, width=15, bg="#313131", textvariable=examDate, fg="#FFFFFF")
        labelExamName.place(x=185, y=50)

        examTimeLOld = Label(frameLeft, width=20, height=2, bg="#313131", text="Exam Time:", fg="#FFFFFF")
        examTimeLOld.place(x=40, y=150)

        labelExamName = Label(frameLeft, height=2, width=15, bg="#313131", textvariable=examTime, fg="#FFFFFF")
        labelExamName.place(x=185, y=150)

        examDurLOld = Label(frameLeft, width=20, height=2, bg="#313131", text="Exam Duration:", fg="#FFFFFF")
        examDurLOld.place(x=40, y=250)

        labelExamName = Label(frameLeft, height=2, width=15, bg="#313131", textvariable=examDuration, fg="#FFFFFF")
        labelExamName.place(x=185, y=250)

        examAtLOld = Label(frameLeft, width=20, height=2, bg="#313131", text="Exam Attempt Number:", fg="#FFFFFF")
        examAtLOld.place(x=40, y=350)

        labelExamName = Label(frameLeft, height=2, width=15, bg="#313131", textvariable=examAttempt, fg="#FFFFFF")
        labelExamName.place(x=185, y=350)

        self.frameRight = Frame(frameCenter, height=470, width=725, bg="#414141", borderwidth=2, relief=SUNKEN)
        self.frameRight.pack(side=LEFT, fill=X)

        examDateL = Label(self.frameRight, width=20, height=3, bg="#313131", text="Exam Date:", fg="#FFFFFF")
        examDateL.place(x=30, y=30)

        today = date.today()
        now = datetime.now()

        self.startDateE = Calendar(self.frameRight, selectmode='day', year=today.year, month=today.month, day=today.day,
                                   date_pattern='dd/mm/yy')
        self.startDateE.place(x=30, y=100)

        examTimeL = Label(self.frameRight, width=20, height=3, bg="#313131", text="Exam Time:", fg="#FFFFFF")
        examTimeL.place(x=350, y=30)

        self.hour_string_time = StringVar()
        self.min_string_time = StringVar()

        self.hour_string_dur = StringVar()
        self.min_string_dur = StringVar()

        self.attemptNum = StringVar()

        f = ('Times', 20)

        self.examTimeHour = Spinbox(self.frameRight, from_=8, to=23, wrap=True, textvariable=self.hour_string_time,
                                    width=2,
                                    state="readonly",
                                    font=f, justify=CENTER)
        self.examTimeMinutes = Spinbox(self.frameRight, from_=0, to=59, wrap=True, textvariable=self.min_string_time,
                                       font=f,
                                       width=2,
                                       justify=CENTER)

        self.examDurHour = Spinbox(self.frameRight, from_=0, to=9, wrap=True, textvariable=self.hour_string_dur,
                                   width=2,
                                   state="readonly",
                                   font=f, justify=CENTER)
        self.examDurMin = Spinbox(self.frameRight, from_=0, to=59, wrap=True, textvariable=self.min_string_dur, font=f,
                                  width=2, justify=CENTER)

        self.examTimeHour.place(x=350, y=100)
        self.examTimeMinutes.place(x=400, y=100)

        examDurL = Label(self.frameRight, width=20, height=3, bg="#313131", text="Exam Duration:", fg="#FFFFFF")
        examDurL.place(x=30, y=300)

        self.examDurHour.place(x=30, y=370)
        self.examDurMin.place(x=80, y=370)

        examAtL = Label(self.frameRight, width=20, height=3, bg="#313131", text="Exam Attempt Number:", fg="#FFFFFF")
        examAtL.place(x=350, y=300)

        self.examAttemptNum = Spinbox(self.frameRight, from_=1, to=10, wrap=True, width=2, state="readonly",
                                      textvariable=self.attemptNum, font=f, justify=CENTER)
        self.examAttemptNum.place(x=350, y=370)

        buttonUpdate = Button(self.frameRight, text="Update", width=13, bg="#ca3e47", fg="#FFFFFF",
                              command=self.checkPassed)
        buttonUpdate.place(x=550, y=200)

    def examCon(self):
        examInfos = self.getExamInfo(self.controller.shared_data["selectedExam"])
        self.startDateE.selection_set(examInfos[2])
        self.hour_string_time.set(examInfos[3][:2])
        self.min_string_time.set(examInfos[3][3:])
        self.hour_string_dur.set(examInfos[1][:2])
        self.min_string_dur.set(examInfos[1][3:])
        self.attemptNum.set(examInfos[0])

        global examDate
        examDate.set(examInfos[2])

        global examTime
        examTime.set(examInfos[3])

        global examDuration
        examDuration.set(examInfos[1])

        global examAttempt
        examAttempt.set(examInfos[0])

    def getExamInfo(self, examID):
        result = db.child("exams").child(examID).get()
        if result.val() is not None:
            resultList = []
            resultList.append(result.val()["AttemptNumbers"])
            resultList.append(result.val()["Duration"])
            resultList.append(result.val()["StartDate"])
            resultList.append(result.val()["StartTime"])
            return resultList
        else:
            return []

    def checkPassed(self):
        today = date.today()

        examDet = self.getExamInfo(self.controller.shared_data["selectedExam"])

        oldExamDate = str(examDet[2]).split("/")

        yearExam = int("20" + oldExamDate[2])
        monthExam = int(oldExamDate[1])
        dayExam = int(oldExamDate[0])

        hourExam = str(examDet[3])[:2]
        minExam = str(examDet[3])[3:]

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        if yearExam < today.year:
            messagebox.showerror("Exam Time Passed", "Exam cannot be updated after the start time")
        elif yearExam > today.year:
            self.updateExam()
        else:
            if monthExam < today.month:
                messagebox.showerror("Exam Time Passed", "Exam cannot be updated after the start time")
            elif monthExam > today.month:
                self.updateExam()
            else:
                if dayExam < today.day:
                    messagebox.showerror("Exam Time Passed", "Exam cannot be updated after the start time")
                elif dayExam > today.day:
                    self.updateExam()
                else:
                    if int(hourExam) < hour:
                        messagebox.showerror("Exam Time Passed", "Exam cannot be updated after the start time")
                    elif int(hourExam) > hour:
                        self.updateExam()
                    else:
                        if int(minExam) <= minute:
                            messagebox.showerror("Exam Time Passed", "Exam cannot be updated after the start time")
                        else:
                            self.updateExam()

    def updateExam(self):
        if len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 1 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str("0" + self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))

        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 1:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + "0" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 1 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str("0" + self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 1 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + "0" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))
        elif len(str(self.examDurHour.get())) == 2 and len(str(self.examDurMin.get())) == 2 and len(
                str(self.examTimeHour.get())) == 2 and len(str(self.examTimeMinutes.get())) == 2:
            self.updateExamDetails(self.controller.shared_data["selectedExam"], str(self.examAttemptNum.get()),
                                   str(self.examDurHour.get() + ":" + self.examDurMin.get()),
                                   str(self.startDateE.get_date()),
                                   str(self.examTimeHour.get() + ":" + self.examTimeMinutes.get()))

    def updateExamDetails(self, examID, attempt, duration, startdate, starttime):
        dateExam = startdate.split("/")
        year = int("20" + dateExam[2])
        month = int(dateExam[0])
        day = int(dateExam[1])

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        today = date.today()

        if str(self.examDurHour.get()) == "0" and (
                str(self.examDurMin.get()) == "0" or str(self.examDurMin.get()) == "00"):
            messagebox.showwarning("Duration 0", "Set the duration")
        elif str(self.examTimeHour.get()) == "0" and (
                str(self.examTimeMinutes.get()) == "0" or str(self.examTimeMinutes.get()) == "00"):
            messagebox.showwarning("Time 0", "Set the Time")
        else:
            if 0 <= int(self.examDurMin.get()) <= 59 and 0 <= int(self.examTimeMinutes.get()) <= 59:
                if year > today.year:
                    db.child("exams").child(examID).update(
                        {"AttemptNumbers": attempt, "Duration": duration,
                         "StartDate": startdate,
                         "StartTime": starttime})
                    messagebox.showinfo("Exam Updated", "Exam Updated")
                    self.controller.get_frame(TeacherCoursePage).exams()
                    self.controller.show_frame(TeacherCoursePage)
                elif year == today.year:
                    if day > today.month:
                        db.child("exams").child(examID).update(
                            {"AttemptNumbers": attempt, "Duration": duration,
                             "StartDate": startdate,
                             "StartTime": starttime})
                        messagebox.showinfo("Exam Updated", "Exam Updated")
                        self.controller.get_frame(TeacherCoursePage).exams()
                        self.controller.show_frame(TeacherCoursePage)
                    elif day == today.month:
                        if month > today.day:
                            db.child("exams").child(examID).update(
                                {"AttemptNumbers": attempt, "Duration": duration,
                                 "StartDate": startdate,
                                 "StartTime": starttime})
                            messagebox.showinfo("Exam Updated", "Exam Updated")
                            self.controller.get_frame(TeacherCoursePage).exams()
                            self.controller.show_frame(TeacherCoursePage)
                        elif month == today.day:
                            if int(self.examTimeHour.get()) > hour:
                                db.child("exams").child(examID).update(
                                    {"AttemptNumbers": attempt, "Duration": duration,
                                     "StartDate": startdate,
                                     "StartTime": starttime})
                                messagebox.showinfo("Exam Updated", "Exam Updated")
                                self.controller.get_frame(TeacherCoursePage).exams()
                                self.controller.show_frame(TeacherCoursePage)
                            elif int(self.examTimeHour.get()) == hour:
                                if int(self.examTimeMinutes.get()) > minute:
                                    db.child("exams").child(examID).update(
                                        {"AttemptNumbers": attempt, "Duration": duration,
                                         "StartDate": startdate,
                                         "StartTime": starttime})
                                    messagebox.showinfo("Exam Updated", "Exam Updated")
                                    self.controller.get_frame(TeacherCoursePage).exams()
                                    self.controller.show_frame(TeacherCoursePage)
                                else:
                                    messagebox.showerror("Time Passed", "Minutes passed")
                            else:
                                messagebox.showerror("Time Passed", "Hour passed")
                        else:
                            messagebox.showwarning("Date Passed", "Select available date")
                    else:
                        messagebox.showwarning("Date Passed", "Select available date")
                else:
                    messagebox.showwarning("Date Passed", "Select available date")
            else:
                messagebox.showerror("Time Error", "Check the minutes")


class TeacherCoursePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        global examsofTeacher
        examsofTeacher = []

        def back():
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)

        global courseAbb
        global courseName

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        courseAbbLabel = Label(frameHeader, height=6, width=20, bg="#313131", textvariable=courseAbb, fg="#FFFFFF")
        courseAbbLabel.pack(side=LEFT)

        courseNameLabel = Label(frameHeader, height=6, width=40, bg="#313131", textvariable=courseName, fg="#FFFFFF")
        courseNameLabel.pack(side=LEFT)

        backButton = Button(frameHeader, text="Back", command=back, width=10,
                            bg="#fed049")
        backButton.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        examFList = Label(frameCenter, height=2, bg="#525252", text="Upcoming Exams", fg="#FFFFFF")
        examFList.pack(side=TOP, fill=X)

        self.frameFutureExams = Frame(frameCenter, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.frameFutureExams.pack(side=TOP, fill=X)

        examPList = Label(frameCenter, height=2, bg="#525252", text="Past Exams", fg="#FFFFFF")
        examPList.pack(side=TOP, fill=X)

        self.framePastExams = Frame(frameCenter, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.framePastExams.pack(side=TOP, fill=X)

        self.exams()

    def exams(self):
        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)

        global examsofTeacher
        examsofTeacher = self.getExamDetailsOfCourse(self.controller.shared_data["selectedCourse"])

        pastExamsCount = 0
        futureExamsCount = 0
        f = ('Times', 30)

        for widget in self.frameFutureExams.winfo_children():
            widget.destroy()

        for widget in self.framePastExams.winfo_children():
            widget.destroy()

        for exam in examsofTeacher:
            splitArrDur = str(exam[3]).split(sep=":")
            lenInMin = int(splitArrDur[0]) * 60 + int(splitArrDur[1])

            tempDelta = timedelta(minutes=lenInMin)

            splitArrDate = str(exam[5]).split(sep="/")
            splitArrTime = str(exam[6]).split(sep=":")
            startTimeE = datetime(int("20" + splitArrDate[2]), int(splitArrDate[1]), int(splitArrDate[0]),
                                  int(splitArrTime[0]), int(splitArrTime[1]))
            startTimeE = startTimeE.replace(tzinfo=tz_IN)

            endTime = startTimeE + tempDelta

            if endTime < datetime_Now:
                pastExamsCount += 1
                self.frameExam = Frame(self.framePastExams, height=200, width=250, bg="#414141", borderwidth=2,
                                       relief=SUNKEN)
                self.frameExam.pack(side=LEFT)

                self.labelExamName = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[0], fg="#FFFFFF")
                self.labelExamName.place(x=25, y=10)

                self.labelExamType = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[4], fg="#FFFFFF")
                self.labelExamType.place(x=25, y=55)

                self.labelExamDate = Label(self.frameExam, height=2, width=28, bg="#313131",
                                           text=str(exam[5] + " " + exam[6]), fg="#FFFFFF")
                self.labelExamDate.place(x=25, y=100)

                self.labelAttNum = Label(self.frameExam, height=2, width=28, bg="#313131",
                                         text=str("Attempt:" + exam[1]), fg="#FFFFFF")
                self.labelAttNum.place(x=25, y=145)

                # self.buttonExam = Button(self.frameExam, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                # command=lambda examID=exam[0]: self.openExamDetail(examID))
                # self.buttonExam.place(x=75, y=160)

            else:
                futureExamsCount += 1
                self.frameExam = Frame(self.frameFutureExams, height=200, width=250, bg="#414141", borderwidth=2,
                                       relief=SUNKEN)
                self.frameExam.pack(side=LEFT)

                self.labelExamName = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[0], fg="#FFFFFF")
                self.labelExamName.place(x=25, y=10)

                self.labelExamType = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[4], fg="#FFFFFF")
                self.labelExamType.place(x=25, y=60)

                self.labelExamDate = Label(self.frameExam, height=2, width=28, bg="#313131",
                                           text=str(exam[5] + " " + exam[6]), fg="#FFFFFF")
                self.labelExamDate.place(x=25, y=110)

                self.buttonExam = Button(self.frameExam, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                                         command=lambda examID=exam[0]: self.openExamDetail(examID))
                self.buttonExam.place(x=75, y=160)

        if pastExamsCount == 0:
            examNoPast = Label(self.framePastExams, height=4, bg="#414141", text="There are no finished exams",
                               fg="#FFFFFF", font=f)
            examNoPast.pack(fill=X, expand=True)
        if futureExamsCount == 0:
            examNoFuture = Label(self.frameFutureExams, height=4, bg="#414141", text="There are no upcoming exams",
                                 fg="#FFFFFF", font=f)
            examNoFuture.pack(fill=X, expand=True)

    def openExamDetail(self, examID):
        self.controller.shared_data["selectedExam"] = examID

        global examAbb
        examAbb.set(self.controller.shared_data["selectedExam"])

        result123 = db.child("exams").child(self.controller.shared_data["selectedExam"]).get()

        global examType
        examType.set(result123.val()["ExamType"])

        self.controller.get_frame(ExamDetailPage).examCon()

        self.controller.show_frame(ExamDetailPage)

    def getExamsOfTeacher(self, teacherMail):
        examsArrays = []

        result = db.child("courses").order_by_child("TeacherMail").equal_to(teacherMail).get()
        result1 = list(result.val())
        # print(result1)
        for course in result1:
            examResult = db.child("exams").order_by_child("CourseID").equal_to(course).get()
            if len(examResult.val()) != 0:
                for exam in examResult:
                    examArray = []
                    examArray.append(exam.key())
                    examArray.append(exam.val()["AttemptNumbers"])
                    examArray.append(exam.val()["CourseID"])
                    examArray.append(exam.val()["Duration"])
                    examArray.append(exam.val()["ExamType"])
                    examArray.append(exam.val()["StartDate"])
                    examArray.append(exam.val()["StartTime"])
                    # print(exam.val())
                    # print(exam.key())
                    examsArrays.append(examArray)

        # print(examsArrays)
        return examsArrays

    def getExamDetailsOfCourse(self, courseID):
        examResult = db.child("exams").order_by_child("CourseID").equal_to(str(courseID)).get()
        # print(examResult.val())
        examsArrays = []
        # examResult = db.child("exams").order_by_child("CourseID").equal_to(course[0]).get()
        if len(examResult.val()) != 0:
            for exam in examResult:
                examArray = []
                examArray.append(exam.key())
                examArray.append(exam.val()["AttemptNumbers"])
                examArray.append(exam.val()["CourseID"])
                examArray.append(exam.val()["Duration"])
                examArray.append(exam.val()["ExamType"])
                examArray.append(exam.val()["StartDate"])
                examArray.append(exam.val()["StartTime"])
                examsArrays.append(examArray)
        return examsArrays


class ExamReports(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        courses = []
        exams = []

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        def back():
            controller.get_frame(TeacherMainPage).courses()
            controller.show_frame(TeacherMainPage)
            self.trv.delete(*self.trv.get_children())
            self.trv2.delete(*self.trv2.get_children())
            self.selectedPath.configure(text="File Path")
            self.coursesExamRepC.set("")
            self.coursesExamRepE.set("")
            self.studentIDLabel.configure(text="")

        self.t1 = StringVar()

        selectCourse = Label(frameHeader, text="Select Course", width=10, height=2, bg="#313131", fg="#FFFFFF")
        selectCourse.place(x=20, y=10)

        self.coursesExamRepC = ttk.Combobox(frameHeader, values=courses, state='readonly', width=30,
                                            postcommand=self.addCourses)
        self.coursesExamRepC.place(x=20, y=50)

        selectExam = Label(frameHeader, text="Select Exam", width=10, height=2, bg="#313131", fg="#FFFFFF")
        selectExam.place(x=250, y=10)

        self.coursesExamRepE = ttk.Combobox(frameHeader, values=exams, state='readonly', width=30,
                                            postcommand=self.addExams)
        self.coursesExamRepE.place(x=250, y=50)

        getDetailsButton = Button(frameHeader, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                                  command=self.completeTable)
        getDetailsButton.place(x=500, y=47)

        backButton = Button(frameHeader, text="Back", command=back, width=10, bg="#fed049")
        backButton.place(x=925, y=35)

        self.frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        self.frameCenter.pack(side=TOP, fill=X)

        self.studentIDLabel = Label(self.frameCenter, width=30, height=1, bg="#414141", fg="#FFFFFF",
                                    font=('Times', 16))
        self.studentIDLabel.place(x=5, y=10)

        frameLeft = Frame(self.frameCenter, height=470, width=625, bg="#414141", borderwidth=2, relief=SUNKEN)
        frameLeft.pack(side=LEFT)

        tabs = ttk.Notebook(frameLeft)
        tabs.pack(fill=BOTH, expand=True)
        tabs1 = Frame(tabs)
        tabs2 = Frame(tabs)
        tabs3 = Frame(tabs)

        tabs.add(tabs1, text='Class Report')
        tabs.add(tabs2, text='Student Detail Table')
        tabs.add(tabs3, text='Student EyeGaze Table')

        studentListL = Label(tabs1, width=100, height=2, bg="#313131", text="Exam Student List", fg="#FFFFFF")
        studentListL.pack(side=TOP)

        self.trv = ttk.Treeview(tabs1, columns=(1, 2, 3, 4, 5, 6), height=10)
        style = ttk.Style(self.trv)
        style.configure('Treeview', rowheight=30)

        self.trv.heading('#0', text="#")
        self.trv.column("#0", minwidth=0, width=15)
        self.trv.heading('#1', text="Student ID")
        self.trv.column("#1", minwidth=0, width=70)
        self.trv.heading('#2', text="Attempt Count")
        self.trv.column("#2", minwidth=0, width=90)
        self.trv.heading('#3', text="Total FaceRec Count")
        self.trv.column("#3", minwidth=0, width=120)
        self.trv.heading('#4', text="False FaceRec Count")
        self.trv.column("#4", minwidth=0, width=120)
        self.trv.heading('#5', text="Missed FaceRec Count")
        self.trv.column("#5", minwidth=0, width=130)
        self.trv.heading('#6', text="isAlone Violation Count")
        self.trv.column("#6", minwidth=0, width=140)

        yscrollbar = ttk.Scrollbar(tabs1, orient="vertical", command=self.trv.yview)

        self.trv.pack(side=LEFT)
        yscrollbar.pack(side="right", fill="y")

        self.trv.configure(yscrollcommand=yscrollbar.set)

        global StudentIDColumn
        StudentIDColumn = []
        global AttemptCount
        AttemptCount = []
        global TotalFaceRecCount
        TotalFaceRecCount = []
        global FalseFaceRecCount
        FalseFaceRecCount = []
        global MissedFaceRecCount
        MissedFaceRecCount = []
        global isAloneVioCount
        isAloneVioCount = []

        self.trv2 = ttk.Treeview(tabs2, columns=(1, 2, 3), height=10)
        style = ttk.Style(self.trv2)
        style.configure('Treeview', rowheight=30)

        self.trv2.heading('#0', text="")
        self.trv2.column("#0", minwidth=0, width=80)
        self.trv2.heading('#1', text="Event Name")
        self.trv2.column("#1", minwidth=0, width=200)
        self.trv2.heading('#2', text="Time Stamp")
        self.trv2.column("#2", minwidth=0, width=200)
        self.trv2.heading('#3', text="Value")
        self.trv2.column("#3", minwidth=0, width=200)

        yscrollbar = ttk.Scrollbar(tabs2, orient="vertical", command=self.trv2.yview)

        self.trv2.pack(side=LEFT)
        yscrollbar.pack(side="right", fill="y")

        self.trv2.configure(yscrollcommand=yscrollbar.set)

        global eventName
        eventName = []
        global timeStamp
        timeStamp = []
        global categoryPart
        categoryPart = []

        self.trv3 = ttk.Treeview(tabs3, columns=(1, 2, 3, 4, 5, 6), height=10)
        style = ttk.Style(self.trv3)
        style.configure('Treeview', rowheight=30)

        self.trv3.heading('#0', text="#")
        self.trv3.column("#0", minwidth=0, width=15)
        self.trv3.heading('#1', text="Student ID")
        self.trv3.column("#1", minwidth=0, width=70)
        self.trv3.heading('#2', text="Attempt Count")
        self.trv3.column("#2", minwidth=0, width=90)
        self.trv3.heading('#3', text="Total FaceRec Count")
        self.trv3.column("#3", minwidth=0, width=120)
        self.trv3.heading('#4', text="False FaceRec Count")
        self.trv3.column("#4", minwidth=0, width=120)
        self.trv3.heading('#5', text="Missed FaceRec Count")
        self.trv3.column("#5", minwidth=0, width=130)
        self.trv3.heading('#6', text="isAlone Violation Count")
        self.trv3.column("#6", minwidth=0, width=140)

        yscrollbar = ttk.Scrollbar(tabs3, orient="vertical", command=self.trv3.yview)

        self.trv3.pack(side=LEFT)
        yscrollbar.pack(side="right", fill="y")

        self.trv3.configure(yscrollcommand=yscrollbar.set)

        self.frameRight = Frame(self.frameCenter, height=500, width=425, bg="#414141", borderwidth=2, relief=SUNKEN)
        self.frameRight.pack(side=LEFT, fill=BOTH)

        self.frameRightBot = Frame(self.frameRight, height=296, width=336, bg="#414141", borderwidth=4, relief=SUNKEN)
        self.frameRightBot.place(x=0, y=200)

        selectPath = Label(self.frameRight, text="Select Path", width=10, height=2, bg="#313131", fg="#FFFFFF")
        selectPath.place(x=135, y=25)

        self.selectedPath = Label(self.frameRight, text="File Path", width=44, height=1, bg="#FFFFFF", fg="#000000")
        self.selectedPath.place(x=10, y=90)

        self.buttons()

    def addCourses(self):
        result = db.child("courses").order_by_child("TeacherMail").equal_to(
            self.controller.shared_data["email"].get()).get()
        result1 = list(result.val())

        self.coursesExamRepC['values'] = result1

    def addExams(self):
        result = db.child("exams").order_by_child("CourseID").equal_to(str(self.coursesExamRepC.get())).get()
        typeList = list()
        for x in result:
            typeList.append(x.val()["ExamType"])
        examList = list(result.val())
        finalList = list()

        for exam, type in zip(examList, typeList):
            result = db.child("examEnroll").child(exam).get()
            if result.val() != None:
                finalList.append(exam + "/" + type)

        self.coursesExamRepE['values'] = finalList

    def completeTable(self):
        if not (str(self.coursesExamRepE.get()).isspace() or len(str(self.coursesExamRepE.get())) == 0 or str(
                self.coursesExamRepE.get()) == ""):
            self.fillTable()
            self.buttonBrowse.configure(state=NORMAL)
            self.studentDetailBut.configure(state=NORMAL)
        else:
            messagebox.showerror("Blank Spaces", "Select exam")

    def fillTable(self):
        self.trv.delete(*self.trv.get_children())

        global StudentIDColumn
        StudentIDColumn.clear()
        global AttemptCount
        AttemptCount.clear()
        global TotalFaceRecCount
        TotalFaceRecCount.clear()
        global FalseFaceRecCount
        FalseFaceRecCount.clear()
        global MissedFaceRecCount
        MissedFaceRecCount.clear()
        global isAloneVioCount
        isAloneVioCount.clear()

        courseABB = str(self.coursesExamRepE.get()).split("/")
        oneExamRep = self.getExamReportTable(courseABB[0])

        StudentIDColumn = oneExamRep[0]
        AttemptCount = oneExamRep[1]
        TotalFaceRecCount = oneExamRep[2]
        FalseFaceRecCount = oneExamRep[3]
        MissedFaceRecCount = oneExamRep[4]
        isAloneVioCount = oneExamRep[5]

        i = 0
        for studentID, attempt, totalFR, falseFR, missedFR, isAloneV in zip(StudentIDColumn, AttemptCount,
                                                                            TotalFaceRecCount, FalseFaceRecCount,
                                                                            MissedFaceRecCount, isAloneVioCount):
            self.trv.insert(parent='', index='end', iid=i, text="",
                            values=(studentID, attempt, totalFR, falseFR, missedFR, isAloneV))
            i += 1

    def getExamReportTable(self, examID):
        studentIDCol = list()
        attemptNumCol = list()
        totalFrCol = list()
        missedFrCol = list()
        falseFrCol = list()
        solVioCol = list()
        result = db.child("examEnroll").child(examID).get()
        for a in result:
            studentIDCol.append(a.key())
            # print(a.key())
            # print(a.val())
            for b in a.val():
                solVioOcc = False
                # print(b)
                # print(a.val()[b])
                if b == "Attempts":
                    # print(len(list(a.val()[b])))
                    attemptNumCol.append(len(list(a.val()[b])))
                elif b == "FrChecks":
                    totalCount = 0
                    missedCount = 0
                    falseCount = 0

                    for c in a.val()[b]:
                        # print(c)
                        # print(a.val()[b][c])
                        if a.val()[b][c]["Status"] == "Missed":
                            missedCount += 1

                        elif a.val()[b][c]["Status"] == "False":
                            falseCount += 1
                        totalCount += 1
                    totalFrCol.append(totalCount)
                    missedFrCol.append(missedCount)
                    falseFrCol.append(falseCount)
                elif b == "Solditute":
                    # print(len(list(a.val()[b])))
                    solVioOcc = True
                    solVioCol.append(len(list(a.val()[b])))
            if solVioOcc == False:
                solVioCol.append(0)
        colsArr = list()
        colsArr.append(studentIDCol)
        colsArr.append(attemptNumCol)
        colsArr.append(totalFrCol)
        colsArr.append(falseFrCol)
        colsArr.append(missedFrCol)
        colsArr.append(solVioCol)

        # print(studentIDCol)
        # print(attemptNumCol)
        # print(totalFrCol)
        # print(falseFrCol)
        # print(missedFrCol)
        # print(solVioCol)
        # print(colsArr)

        return colsArr

    def givePath(self):
        self.filename = filedialog.askdirectory(initialdir="/", title='Please select a directory')

        if len(self.filename) == 0:
            messagebox.showwarning("Empty Directory", "Please select a directory.")
            self.selectedPath.configure(text="File Path")
            self.downMedia.configure(state=DISABLED)
            self.downAllMedia.configure(state=DISABLED)
            self.eyeGazeDetail.configure(state=DISABLED)

        else:
            self.selectedPath.configure(text=self.filename)
            self.downMedia.configure(state=NORMAL)
            self.downAllMedia.configure(state=NORMAL)
            self.eyeGazeDetail.configure(state=NORMAL)

    def buttons(self):
        self.buttonBrowse = Button(self.frameRight, text="Browse", width=10, bg="#ca3e47", fg="#FFFFFF",
                                   state=DISABLED, command=self.givePath)
        self.buttonBrowse.place(x=135, y=150)

        self.downMedia = Button(self.frameRightBot, text="Download Student Media", width=20, bg="#ca3e47", fg="#FFFFFF",
                                state=DISABLED, command=self.downloadMedia)
        self.downMedia.place(x=90, y=50)

        self.downAllMedia = Button(self.frameRightBot, text="Download All Students Media", width=25, bg="#ca3e47",
                                   fg="#FFFFFF", state=DISABLED, command=self.downloadAllMedia)
        self.downAllMedia.place(x=70, y=125)

        self.studentDetailBut = Button(self.frameRightBot, text="Show Student Details", width=20, bg="#ca3e47",
                                       fg="#FFFFFF", state=DISABLED, command=self.studentDetails)
        self.studentDetailBut.place(x=90, y=200)

    def downloadFilesOfStudent(self, folderPath, examID, studentID):
        # WAIT FOR DOWNLOAD EKRANINI THREADLE ÇALIŞTIRACAK, GLOBAL STATE İLE BİRBİRLERİNİ BİTİRECEKLER.
        result = db.child("examEnroll").child(examID).child(studentID).get()
        folderpath = Path(f"{folderPath}", studentID).__str__()
        # print(folderpath1)
        # folderpath = Path(r"C:\Users\KORHAN.KOZ\Desktop\Downloads", studentID).__str__()
        # print(folderpath)
        os.mkdir(folderpath)
        for a in result:
            # print(a.key())
            # print(a.val())
            if a.key() == "Attempts":
                for b in a.val():
                    # print(a.val()[b]["PathToImg"])
                    storage.child("/" + a.val()[b]["PathToImg"]).download(path="ImagesBasic", filename=b + ".png")
                    parent = Path(__file__).parent
                    initPath = Path(parent, b + ".png").__str__()
                    destPath = Path(folderpath).__str__()
                    shutil.move(initPath, destPath)
            if a.key() == "FrChecks":
                # Write handle for missed FR Checks
                for b in a.val():
                    # print(a.val()[b]["PathToImg"])
                    if a.val()[b]["Status"] != "Missed":
                        storage.child("/" + a.val()[b]["PathToImg"]).download(path="ImagesBasic", filename=b + ".png")
                        parent = Path(__file__).parent
                        initPath = Path(parent, b + ".png").__str__()
                        destPath = Path(folderpath).__str__()
                        shutil.move(initPath, destPath)
            if a.key() == "VidRec":
                for b in a.val():
                    # print(a.val()[b]["PathToVid"])
                    storage.child("/" + a.val()[b]["PathToVid"]).download(path="ImagesBasic", filename=b + ".mp4")
                    parent = Path(__file__).parent
                    initPath = Path(parent, b + ".mp4").__str__()
                    destPath = Path(folderpath).__str__()
                    shutil.move(initPath, destPath)

    def downloadMedia(self):
        try:
            rowStudentID = self.getrow()
            courseIDS = str(self.coursesExamRepE.get()).split("/")
            self.downloadFilesOfStudent(self.selectedPath.cget("text"), courseIDS[0], rowStudentID)
            messagebox.showinfo("Media Downloaded", "Execution completed")
        except:
            messagebox.showerror("Empty Student", "Student not selected")

    def getrow(self):
        # rowid = trv.identify_row(event.y)
        item = self.trv.item(self.trv.focus())
        self.t1.set(item['values'][0])
        return self.t1.get()

    def downloadAllMedia(self):
        courseIDS = str(self.coursesExamRepE.get()).split("/")

        self.downloadAllStudents(self.selectedPath.cget("text"), courseIDS[0])
        messagebox.showinfo("Media Files Downloaded", "Execution completed")

    def downloadAllStudents(self, folderPath, examID):
        folderpath1 = Path(f"{folderPath}", examID).__str__()
        os.mkdir(folderpath1)
        result = db.child("examEnroll").child(examID).get()
        stuList = list()
        for a in result:
            stuList.append(a.key())
        for a in stuList:
            self.downloadFilesOfStudent(folderpath1, examID, a)

    def getDetailedReportTable(self, examID, studentID):
        finalArr = list()
        eventNameCol = list()
        timestampCol = list()
        categoryCol = list()
        result = db.child("examEnroll").child(examID).child(studentID).get()
        for a in result:
            if a.key() == "Attempts":
                for b in a.val():
                    eventNameCol.append(b)
                    timestampCol.append(a.val()[b]["TimeStamp"])
                    categoryCol.append(a.key())
            if a.key() == "FrChecks":
                for b in a.val():
                    eventNameCol.append(b)
                    if a.val()[b]["Status"] != "Missed":
                        timestampCol.append(a.val()[b]["TimeStamp"])
                    else:
                        timestampCol.append("-")
                    categoryCol.append(a.key())
            if a.key() == "Solditute":
                for b in a.val():
                    eventNameCol.append(b)
                    timestampCol.append(a.val()[b]["TimeStamp"])
                    categoryCol.append(a.key())

        finalArr.append(eventNameCol)
        finalArr.append(timestampCol)
        finalArr.append(categoryCol)

        return finalArr

    def studentDetails(self):
        self.trv2.delete(*self.trv2.get_children())

        global eventName
        eventName.clear()
        global timeStamp
        timeStamp.clear()
        global categoryPart
        categoryPart.clear()

        try:
            courseIDS = str(self.coursesExamRepE.get()).split("/")
            rowStudentID = self.getrow()

            self.studentIDLabel.configure(text="Selected Student: " + str(rowStudentID))

            table2data = self.getDetailedReportTable(courseIDS[0], rowStudentID)

            eventName = table2data[0]
            timeStamp = table2data[1]
            categoryPart = table2data[2]

            i = 0
            for event, timestampTS, categoryProduct in zip(eventName, timeStamp, categoryPart):
                self.trv2.insert(parent='', index='end', iid=i, text="",
                             values=(event, timestampTS, categoryProduct))
                i += 1
        except:
            messagebox.showerror("Empty Student", "Select a Student")


# STUDENT PAGES


class ExamDetailStudent(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        def back():
            controller.get_frame(CoursePageS).examsS()
            controller.show_frame(CoursePageS)

        global examAbbS
        examAbbS = tk.StringVar()

        global examTypeS
        examTypeS = tk.StringVar()

        global examDateS
        examDateS = tk.StringVar()

        global examTimeS
        examTimeS = tk.StringVar()

        global examDurationS
        examDurationS = tk.StringVar()

        global examAttemptS
        examAttemptS = tk.StringVar()

        self.examAbbLabel = Label(frameHeader, height=8, width=20, bg="#313131", textvariable=examAbbS, fg="#FFFFFF")
        self.examAbbLabel.pack(side=LEFT)

        examTypeLabel = Label(frameHeader, height=8, width=40, bg="#313131", textvariable=examTypeS, fg="#FFFFFF")
        examTypeLabel.pack(side=LEFT)

        backButton = Button(frameHeader, text="Back", command=back, width=10, bg="#fed049")
        backButton.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        examNameLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Name:", fg="#FFFFFF")
        examNameLS.place(x=200, y=60)

        labelExamNameS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examAbbS, fg="#FFFFFF")
        labelExamNameS.place(x=345, y=60)

        examTypeLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Type:", fg="#FFFFFF")
        examTypeLS.place(x=600, y=60)

        labelExamTypeS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examTypeS, fg="#FFFFFF")
        labelExamTypeS.place(x=745, y=60)

        examDateLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Date:", fg="#FFFFFF")
        examDateLS.place(x=200, y=160)

        labelExamDateS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examDateS, fg="#FFFFFF")
        labelExamDateS.place(x=345, y=160)

        examTimeLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Time:", fg="#FFFFFF")
        examTimeLS.place(x=600, y=160)

        labelExamTimeS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examTimeS, fg="#FFFFFF")
        labelExamTimeS.place(x=745, y=160)

        examDurLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Duration:", fg="#FFFFFF")
        examDurLS.place(x=200, y=260)

        labelExamDurS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examDurationS, fg="#FFFFFF")
        labelExamDurS.place(x=345, y=260)

        examAtLS = Label(frameCenter, width=20, height=2, bg="#313131", text="Exam Attempt Number:", fg="#FFFFFF")
        examAtLS.place(x=600, y=260)

        labelExamAtS = Label(frameCenter, height=2, width=15, bg="#313131", textvariable=examAttemptS, fg="#FFFFFF")
        labelExamAtS.place(x=745, y=260)

        buttonExam = Button(frameCenter, text="Enter", width=13, bg="#ca3e47", fg="#FFFFFF", command=self.enterExam)
        buttonExam.place(x=480, y=360)

    def examCon(self):
        examInfos = self.getExamInfo(self.controller.shared_data["selectedExam"])

        global examDateS
        examDateS.set(examInfos[2])

        global examTimeS
        examTimeS.set(examInfos[3])

        global examDurationS
        examDurationS.set(examInfos[1])

        global examAttemptS
        examAttemptS.set(examInfos[0])

        global examTypeS
        examTypeS.set(examInfos[4])

        global examAbbS
        examAbbS.set(examInfos[5])

    def getExamInfo(self, examID):
        result = db.child("exams").child(examID).get()
        if result.val() is not None:
            resultList = []
            resultList.append(result.val()["AttemptNumbers"])
            resultList.append(result.val()["Duration"])
            resultList.append(result.val()["StartDate"])
            resultList.append(result.val()["StartTime"])
            resultList.append(result.val()["ExamType"])
            resultList.append(result.key())
            return resultList
        else:
            return []

    def getIDfromMailS(self, mail):
        resultIDS = db.child("students").order_by_child("email").equal_to(mail).get()
        studentID = list(resultIDS.val())[0]
        return studentID

    def enterExam(self):
        currentExam = self.getExamInfo(self.controller.shared_data["selectedExam"])

        startDate = currentExam[2]
        startTime = currentExam[3]
        duration = currentExam[1]
        attempNum = currentExam[0]

        splitArrDur = duration.split(sep=":")
        lenInMin = int(splitArrDur[0]) * 60 + int(splitArrDur[1])

        tempDelta = timedelta(minutes=lenInMin)

        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)

        splitArrDate = startDate.split(sep="/")
        splitArrTime = startTime.split(sep=":")
        startTimeE = datetime(int("20" + splitArrDate[2]), int(splitArrDate[1]), int(splitArrDate[0]),
                              int(splitArrTime[0]), int(splitArrTime[1]))
        startTimeE = startTimeE.replace(tzinfo=tz_IN)

        endTime = startTimeE + tempDelta

        studentID = self.getIDfromMailS(self.controller.shared_data["email"].get())

        resultExamEn = db.child("examEnroll").child(self.controller.shared_data["selectedExam"]).child(studentID).child(
            "Attempts").get()
        # print(len(resultExamEn.val()))

        if datetime_Now > startTimeE:
            if datetime_Now < endTime:
                if resultExamEn.val() is not None:
                    if len(resultExamEn.val()) < int(attempNum):
                        self.faceRecog(self.getIDfromMailS(self.controller.shared_data["email"].get()),
                                       self.controller.shared_data["selectedExam"])
                    else:
                        messagebox.showerror("Lack of Attempt", "No more attempts allowed")
                else:
                    self.faceRecog(self.getIDfromMailS(self.controller.shared_data["email"].get()),
                                   self.controller.shared_data["selectedExam"])
            else:
                messagebox.showerror("Exam Date Error", "Exam ended")
        else:
            messagebox.showerror("Exam Date Error", "Exam has not started yet")

    def faceRecog(self, studentID, ExamID):
        countOfSucces = 0
        result = db.child("students").child(studentID).get()
        faceEncoding = np.asarray(result.val()["encoding"])
        resultExamEn = db.child("examEnroll").child(ExamID).child(studentID).child("Attempts").get()
        # print(resultExamEn.val())
        attemptImg = None
        cap = cv2.VideoCapture(0)
        escapecondition = True

        while True:
            k = cv2.waitKey(1)

            if k % 256 == 27:
                # ESC pressed
                escapecondition = False
                # print("Escape hit, closing...")
                break
            success, img = cap.read()
            if not success:
                # print("failed to grab frame")
                break
            if countOfSucces == 5:
                attemptImg = img
                break

            cv2.imshow("test", img)
            imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgSmall)
            # print(len(facesCurFrame))
            # print(facesCurFrame)
            encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)
            # print(encodesCurFrame)
            if len(encodesCurFrame) == 1:
                matches = face_recognition.compare_faces(faceEncoding, encodesCurFrame, 0.56)
                # print(matches[0])
                if matches[0]:
                    countOfSucces = countOfSucces + 1

            cv2.waitKey(1)

        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)

        if escapecondition:
            # print("Recognition Successful")
            if resultExamEn.val() is None:
                parent = Path(__file__).parent
                registerPic = Path(parent, 'Temp', 'TempAttImg.png').__str__()
                cv2.imwrite(registerPic, attemptImg)
                path_on_cloud = ExamID + "/" + studentID + "/" + "Attempt-1"
                storage.child(path_on_cloud).put(registerPic)

                data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                db.child("examEnroll").child(ExamID).child(studentID).child("Attempts").child("Attempt-1").set(data1)
            else:
                # print(resultExamEn.val())
                # print(len(resultExamEn.val()))

                parent = Path(__file__).parent
                registerPic = Path(parent, 'Temp', 'TempAttImg.png').__str__()
                cv2.imwrite(registerPic, attemptImg)
                # print(str(len(resultExamEn.val())))
                path_on_cloud = ExamID + "/" + studentID + "/" + "Attempt-" + str(1 + len(resultExamEn.val()))
                storage.child(path_on_cloud).put(registerPic)

                data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                db.child("examEnroll").child(ExamID).child(studentID).child("Attempts").child(
                    "Attempt-" + str(1 + len(resultExamEn.val()))).set(data1)
            self.controller.show_frame(ExamPageS)

        cap.release()
        cv2.destroyAllWindows()


class CoursePageS(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        def back():
            controller.get_frame(StudentMainPage).coursesS()
            controller.show_frame(StudentMainPage)

        global examsofStudent
        examsofStudent = []

        global courseAbb
        global courseName

        frameHeader = Frame(self, height=100, width=1350, bg="#313131", padx=20, relief=SUNKEN, borderwidth=2)
        frameHeader.pack(side=TOP, fill=X)

        courseAbbLabel = Label(frameHeader, height=6, width=20, bg="#313131", textvariable=courseAbb, fg="#FFFFFF")
        courseAbbLabel.pack(side=LEFT)

        courseNameLabel = Label(frameHeader, height=6, width=40, bg="#313131", textvariable=courseName, fg="#FFFFFF")
        courseNameLabel.pack(side=LEFT)

        backButton = Button(frameHeader, text="Back", command=back, width=10,
                            bg="#fed049")
        backButton.pack(side=RIGHT)

        frameCenter = Frame(self, width=1350, relief=RIDGE, bg="#414141", height=680)
        frameCenter.pack(side=TOP, fill=X)

        examFList = Label(frameCenter, height=2, bg="#525252", text="Upcoming Exams", fg="#FFFFFF")
        examFList.pack(side=TOP, fill=X)

        self.frameFutureExams = Frame(frameCenter, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.frameFutureExams.pack(side=TOP, fill=X)

        examPList = Label(frameCenter, height=2, bg="#525252", text="Past Exams", fg="#FFFFFF")
        examPList.pack(side=TOP, fill=X)

        self.framePastExams = Frame(frameCenter, height=250, width=1350, bg="#313131", relief=SUNKEN)
        self.framePastExams.pack(side=TOP, fill=X)

        self.examsS()

    def getIDfromMail(self, mail):
        result = db.child("students").order_by_child("email").equal_to(mail).get()
        studentID = ""
        # print(result.val())
        if len(result.val()) != 0:
            studentID = list(result.val())[0]
        # print(studentID)
        return studentID

    def examsS(self):
        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)

        global examsofStudent
        examsofStudent = self.getExamDetailsOfCourse(self.controller.shared_data["selectedCourse"])

        pastExamsCount = 0
        futureExamsCount = 0
        f = ('Times', 30)

        for widget in self.frameFutureExams.winfo_children():
            widget.destroy()

        for widget in self.framePastExams.winfo_children():
            widget.destroy()

        for exam in examsofStudent:
            splitArrDur = str(exam[3]).split(sep=":")
            lenInMin = int(splitArrDur[0]) * 60 + int(splitArrDur[1])

            tempDelta = timedelta(minutes=lenInMin)

            splitArrDate = str(exam[5]).split(sep="/")
            splitArrTime = str(exam[6]).split(sep=":")
            startTimeE = datetime(int("20" + splitArrDate[2]), int(splitArrDate[1]), int(splitArrDate[0]),
                                  int(splitArrTime[0]), int(splitArrTime[1]))
            startTimeE = startTimeE.replace(tzinfo=tz_IN)

            endTime = startTimeE + tempDelta

            if endTime < datetime_Now:
                pastExamsCount += 1
                self.frameExam = Frame(self.framePastExams, height=200, width=250, bg="#414141", borderwidth=2,
                                       relief=SUNKEN)
                self.frameExam.pack(side=LEFT)

                self.labelExamName = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[0], fg="#FFFFFF")
                self.labelExamName.place(x=25, y=10)

                self.labelExamType = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[4], fg="#FFFFFF")
                self.labelExamType.place(x=25, y=60)

                self.labelExamDate = Label(self.frameExam, height=2, width=28, bg="#313131",
                                           text=str(exam[5] + " " + exam[6]), fg="#FFFFFF")
                self.labelExamDate.place(x=25, y=110)

                # self.buttonExam = Button(self.frameExam, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                # command=lambda examID=exam[0]: self.openExamDetail(examID))
                # self.buttonExam.place(x=75, y=160)

            else:
                futureExamsCount += 1
                self.frameExam = Frame(self.frameFutureExams, height=200, width=250, bg="#414141", borderwidth=2,
                                       relief=SUNKEN)
                self.frameExam.pack(side=LEFT)

                self.labelExamName = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[0], fg="#FFFFFF")
                self.labelExamName.place(x=25, y=10)

                self.labelExamType = Label(self.frameExam, height=2, width=28, bg="#313131", text=exam[4], fg="#FFFFFF")
                self.labelExamType.place(x=25, y=60)

                self.labelExamDate = Label(self.frameExam, height=2, width=28, bg="#313131",
                                           text=str(exam[5] + " " + exam[6]), fg="#FFFFFF")
                self.labelExamDate.place(x=25, y=110)

                self.buttonExam = Button(self.frameExam, text="Details", width=13, bg="#ca3e47", fg="#FFFFFF",
                                         command=lambda examID=exam[0]: self.openExamDetail(examID))
                self.buttonExam.place(x=75, y=160)

        if pastExamsCount == 0:
            examNoPast = Label(self.framePastExams, height=4, bg="#414141", text="There are no finished exams",
                               fg="#FFFFFF", font=f)
            examNoPast.pack(fill=X, expand=True)
        if futureExamsCount == 0:
            examNoFuture = Label(self.frameFutureExams, height=4, bg="#414141", text="There are no upcoming exams",
                                 fg="#FFFFFF", font=f)
            examNoFuture.pack(fill=X, expand=True)

    def getExamDetailsOfCourse(self, courseID):
        examResult = db.child("exams").order_by_child("CourseID").equal_to(str(courseID)).get()
        # print(examResult.val())
        examsArrays = []
        # examResult = db.child("exams").order_by_child("CourseID").equal_to(course[0]).get()
        if len(examResult.val()) != 0:
            for exam in examResult:
                examArray = []
                examArray.append(exam.key())
                examArray.append(exam.val()["AttemptNumbers"])
                examArray.append(exam.val()["CourseID"])
                examArray.append(exam.val()["Duration"])
                examArray.append(exam.val()["ExamType"])
                examArray.append(exam.val()["StartDate"])
                examArray.append(exam.val()["StartTime"])
                examsArrays.append(examArray)
        return examsArrays

    def openExamDetail(self, examID):
        self.controller.shared_data["selectedExam"] = examID

        global examAbb
        examAbb.set(self.controller.shared_data["selectedExam"])

        result123 = db.child("exams").child(self.controller.shared_data["selectedExam"]).get()

        global examType
        examType.set(result123.val()["ExamType"])

        self.controller.get_frame(ExamDetailStudent).examCon()

        self.controller.show_frame(ExamDetailStudent)

    def getIDfromMailS(self, mail):
        resultIDS = db.child("students").order_by_child("email").equal_to(mail).get()
        studentID = list(resultIDS.val())[0]
        return studentID


class ExamPageS(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#414141")
        self.controller = controller

        global ExitButtonState
        ExitButtonState = False

        def back():
            global ExitButtonState
            ExitButtonState = True
            controller.get_frame(StudentMainPage).coursesS()
            controller.show_frame(StudentMainPage)

        buttonStart = Button(self, text="Start Exam", command=self.exam, fg="white",
                             bg="#ca3e47", width=10)
        buttonStart.grid(row=7, column=1, columnspan=3, padx=10, pady=10)

        buttonExit = Button(self, text="Exit Exam", command=back, fg="white", bg="#ca3e47", width=10)
        buttonExit.grid(row=9, column=1, columnspan=3, padx=10, pady=10)

    def exam(self):
        global examAbbS
        global examDateS
        global examTimeS
        global examDurationS
        if self.controller.shared_data["email"].get() != "Email":
            stuID = self.controller.get_frame(ExamDetailStudent).getIDfromMailS(
                self.controller.shared_data["email"].get())
            t11 = Thread(target=self.threadingS,
                         args=[examDateS.get(), examTimeS.get(), examDurationS.get(), stuID, examAbbS.get()])
            t11.start()
            # self.threadingS(examDateS.get(), examTimeS.get(), examDurationS.get(), stuID, examAbbS.get())

    def threadingS(self, startDate, startTime, duration, studentID, examID):
        global lastTimeSolErrOcc
        global ExitButtonState
        ExitButtonState = False
        lastTimeSolErrOcc = 0
        # get Encoings of the student
        result = db.child("students").child(studentID).get()
        faceEncoding = np.asarray(result.val()["encoding"])
        # Call work function

        # Get timezone obj for Istanbul
        tz_NY = pytz.timezone('Asia/Beirut')
        tz_IN = pytz.timezone('Etc/GMT-3')
        i = 0
        splitArrDate = startDate.split(sep="/")
        splitArrTime = startTime.split(sep=":")
        startTime = datetime(int("20" + splitArrDate[2]), int(splitArrDate[1]), int(splitArrDate[0]),
                             int(splitArrTime[0]), int(splitArrTime[1]))
        startTime = startTime.replace(tzinfo=tz_IN)
        # print(startTime)
        # print(startTime + timedelta(minutes=6))
        # print(type(startTime))
        gaze = GazeTracking()
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # create a array for check times and check status.
        frCheckTimes = []
        # for determination of the frequency of the checks
        splitArrDur = duration.split(sep=":")
        lenInMin = int(splitArrDur[0]) * 60 + int(splitArrDur[1])

        tempDelta1 = timedelta(minutes=lenInMin)
        endTime = startTime + tempDelta1
        # print(endTime, "!!")

        t3 = Thread(target=self.captureVid2, args=[cap, endTime])
        t3.start()

        for i in range(0, 9):
            tempDelta = timedelta(minutes=(i + 1) * lenInMin / 10)
            # print((startTime + tempDelta).time())
            frCheckTimes.append([(startTime + tempDelta), False])

        # print(frCheckTimes)
        datetime_NowArr = datetime.now(tz_IN)
        indexForFR = 1
        for a in frCheckTimes:
            # print(indexForFR)
            if (datetime_NowArr - a[0]) > timedelta(minutes=1):
                a[1] = True
                if (db.child("examEnroll").child(examID).child(studentID).child("FrChecks").child(
                        "FR-" + str(indexForFR)).get().val() is None):
                    data1 = {"PathToImg": "", "Status": "Missed"}
                    db.child("examEnroll").child(examID).child(studentID).child("FrChecks").child(
                        "FR-" + str(indexForFR)).set(data1)
            indexForFR = indexForFR + 1

        # print(frCheckTimes)
        resultOnGoing = db.child(examID).child(studentID).child("FrChecks").get()

        t3 = Thread(target=self.captureEyeGaze, args=[cap, gaze, endTime])
        t4 = Thread(target=self.checkEyeGaze, args=[gaze, endTime, studentID, examID, startTime])

        t3.start()
        t4.start()

        while True:
            success, img = cap.read()
            datetime_Now = datetime.now(tz_IN)
            # print("Real time:", datetime_Now.strftime("%H:%M:%S"))
            # print(type(datetime_Now))
            # print("-----------------------------------------------")
            if (datetime_Now - endTime).days == 0:
                # print("EXAM OVER")
                break
            if ExitButtonState:
                break
            # Thread that checks if there are two or more faces in the img

            t2 = Thread(target=self.work2, args=[img, studentID, examID])
            t2.start()
            t2.join()
            for a in frCheckTimes:
                # print(a[0])
                # print(datetime_Now)
                # print((datetime_Now -a[0]).seconds/60)
                # print((datetime_Now - a[0]).days)
                # print((datetime_Now-a[0])>timedelta(minutes=1))
                # print()
                if (datetime_Now - a[0]).days == 0 and a[1] == False:
                    # print("Starting FR for", a[0], " Time is:", datetime_Now)
                    t1 = Thread(target=self.work, args=[cap, faceEncoding, studentID, examID])
                    t1.start()
                    # t1.join()
                    a[1] = True
                    # print(frCheckTimes)

            # print((frCheckTimes))

            # t1 = Thread(target=work, args=[img,i])
            # t2 = Thread(target=work2, args=[img,i])
            # t1.start()
            # t2.start()
            i = i + 1

        cap.release()
        cv2.destroyAllWindows()
        time.sleep(10)

        resultVidRec = db.child("examEnroll").child(examID).child(studentID).child("VidRec").get()
        if resultVidRec.val() is None:
            parent = Path(__file__).parent
            VidPath = Path(parent, 'videoCap', 'MEST' + '.mp4').__str__()
            path_on_cloudFürVid = examID + "/" + studentID + "/" + "Rec-1"
            storage.child(path_on_cloudFürVid).put(VidPath)

            data1 = {"PathToVid": path_on_cloudFürVid}
            db.child("examEnroll").child(examID).child(studentID).child("VidRec").child("Rec-1").set(data1)
        else:
            numOfRec = 1 + len(list(resultVidRec.val()))
            parent = Path(__file__).parent
            VidPath = Path(parent, 'videoCap', 'MEST' + '.mp4').__str__()
            path_on_cloudFürVid = examID + "/" + studentID + "/" + "Rec-" + str(numOfRec)
            storage.child(path_on_cloudFürVid).put(VidPath)

            data1 = {"PathToVid": path_on_cloudFürVid}
            db.child("examEnroll").child(examID).child(studentID).child("VidRec").child("Rec-" + str(numOfRec)).set(
                data1)

        messagebox.showinfo("Exam Over", "Exam Over")
        self.controller.get_frame(StudentMainPage).coursesS()
        self.controller.show_frame(StudentMainPage)

    def work(self, cap, faceEncoding, studentID, examID):
        # print("sleep time start")
        successState = False
        successImg = None
        nonsuccessImg = None
        countOfSucces = 0

        tryCount = 0
        while True:
            success, img = cap.read()
            if not success:
                # print("failed to grab frame")
                break
            if countOfSucces == 5:
                successState = True
                break
            if tryCount == 50:
                # print("Recog failed and reported.")
                break
            imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgSmall)
            # print(len(facesCurFrame))
            # print(facesCurFrame)
            encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)
            # print(encodesCurFrame)
            if len(encodesCurFrame) == 1:
                matches = face_recognition.compare_faces(faceEncoding, encodesCurFrame, 0.56)
                # print(matches[0])
                if matches[0]:
                    successImg = img
                    countOfSucces = countOfSucces + 1
                    tryCount = tryCount + 1
                else:
                    nonsuccessImg = img
                    tryCount = tryCount + 1
            else:
                nonsuccessImg = img
                tryCount = tryCount + 1

        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)

        resultForFR = db.child("examEnroll").child(examID).child(studentID).child("FrChecks").get()
        if resultForFR.val() is None:
            parent = Path(__file__).parent
            registerPic = Path(parent, 'Temp', 'TempAttImg.png').__str__()
            if successState:
                cv2.imwrite(registerPic, successImg)
            else:
                cv2.imwrite(registerPic, nonsuccessImg)

            path_on_cloud = examID + "/" + studentID + "/" + "FR-1"
            storage.child(path_on_cloud).put(registerPic)

            data1 = {"PathToImg": path_on_cloud, "Status": successState, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
            db.child("examEnroll").child(examID).child(studentID).child("FrChecks").child("FR-1").set(data1)
        else:
            # print(resultExamEn.val())
            # print(len(resultExamEn.val()))

            parent = Path(__file__).parent
            registerPic = Path(parent, 'Temp', 'TempAttImg.png').__str__()
            if successState:
                cv2.imwrite(registerPic, successImg)
            else:
                cv2.imwrite(registerPic, nonsuccessImg)

            path_on_cloud = examID + "/" + studentID + "/" + "FR-" + str(1 + len(resultForFR.val()))
            storage.child(path_on_cloud).put(registerPic)

            data1 = {"PathToImg": path_on_cloud, "Status": successState, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
            db.child("examEnroll").child(examID).child(studentID).child("FrChecks").child(
                "FR-" + str(1 + len(resultForFR.val()))).set(data1)

            # cv2.waitKey(1)

        # parent = Path(__file__).parent
        # print(parent)
        # registerPic = Path(parent, 'Temp', 'TEST-'+str(numOfImg)+'.png').__str__()
        # print(registerPic)
        # cv2.imwrite(registerPic, img)

        # print("sleep time stop")

    def work2(self, img, studentID, examID):
        # imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        # imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
        tz_IN = pytz.timezone('Etc/GMT-3')
        datetime_Now = datetime.now(tz_IN)
        global lastTimeSolErrOcc
        # print(lastTimeSolErrOcc, "!!!!!")

        facesCurFrame = face_recognition.face_locations(img)
        # print(len(facesCurFrame))
        # print(facesCurFrame)
        # encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)
        # print(encodesCurFrame)
        # print(len(facesCurFrame))

        if lastTimeSolErrOcc == 0:
            # print("Time constraint 1 is ok entering the if")
            if len(facesCurFrame) > 1:
                resultExamSol = db.child("examEnroll").child(examID).child(studentID).child("Solditute").get()
                if resultExamSol.val() is None:
                    # print("THERE ARE 2 PEOPLE IN THE IMAGE")
                    lastTimeSolErrOcc = datetime_Now
                    parent = Path(__file__).parent
                    registerPic = Path(parent, 'Temp', 'SecPeop.png').__str__()
                    cv2.imwrite(registerPic, img)
                    path_on_cloud = examID + "/" + studentID + "/" + "Solditute" + "/" + "Violation-1"
                    storage.child(path_on_cloud).put(registerPic)
                    # print("Sent IMG FIRST WAY")

                    data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                    db.child("examEnroll").child(examID).child(studentID).child("Solditute").child("Violation-1").set(
                        data1)


                else:
                    lastTimeSolErrOcc = datetime_Now
                    parent = Path(__file__).parent
                    registerPic = Path(parent, 'Temp', 'SecPeop.png').__str__()
                    cv2.imwrite(registerPic, img)
                    path_on_cloud = examID + "/" + studentID + "/" + "Solditute" + "/" + "Violation-" + str(
                        1 + len(resultExamSol.val()))
                    storage.child(path_on_cloud).put(registerPic)

                    data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                    db.child("examEnroll").child(examID).child(studentID).child("Solditute").child(
                        "Violation-" + str(1 + len(resultExamSol.val()))).set(data1)
        elif (datetime_Now - lastTimeSolErrOcc) > timedelta(minutes=0.5):
            # print("Time constraint 2 is ok entering the if")
            if len(facesCurFrame) > 1:
                resultExamSol = db.child("examEnroll").child(examID).child(studentID).child("Solditute").get()
                if resultExamSol.val() is None:
                    lastTimeSolErrOcc = datetime_Now
                    # print("THERE ARE 2 PEOPLE IN THE IMAGE")
                    parent = Path(__file__).parent
                    registerPic = Path(parent, 'Temp', 'SecPeop.png').__str__()
                    cv2.imwrite(registerPic, img)
                    path_on_cloud = examID + "/" + studentID + "/" + "Solditute" + "/" + "Violation-1"
                    storage.child(path_on_cloud).put(registerPic)
                    # print("Sent IMG SECOND WAY")
                    # print(resultExamSol.val())
                    # print("*****************************")

                    data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                    db.child("examEnroll").child(examID).child(studentID).child("Solditute").child("Violation-1").set(
                        data1)


                else:
                    lastTimeSolErrOcc = datetime_Now
                    parent = Path(__file__).parent
                    registerPic = Path(parent, 'Temp', 'SecPeop.png').__str__()
                    cv2.imwrite(registerPic, img)
                    path_on_cloud = examID + "/" + studentID + "/" + "Solditute" + "/" + "Violation-" + str(
                        1 + len(resultExamSol.val()))
                    storage.child(path_on_cloud).put(registerPic)

                    data1 = {"PathToImg": path_on_cloud, "TimeStamp": datetime_Now.strftime("%H:%M:%S")}
                    db.child("examEnroll").child(examID).child(studentID).child("Solditute").child(
                        "Violation-" + str(1 + len(resultExamSol.val()))).set(data1)

    def captureVid2(self, cap, endTime):
        # cap = cv2.VideoCapture(0)
        parent = Path(__file__).parent
        VidPath = Path(parent, 'videoCap', 'MEST' + '.mp4').__str__()
        vid_cod = cv2.VideoWriter_fourcc(*'FMP4')
        output = cv2.VideoWriter(VidPath, vid_cod, 3.0, (640, 480))
        tz_IN = pytz.timezone('Etc/GMT-3')
        while True:
            success, img = cap.read()
            # cv2.waitKey(1)
            output.write(img)
            datetime_Now = datetime.now(tz_IN)
            if (datetime_Now - endTime).days == 0:
                # print("EXAM OVER")
                break
            if ExitButtonState:
                break
        cap.release()
        # close the already opened file
        output.release()

    def captureEyeGaze(self, cap, gaze, endTime):

        while True:
            tz_IN = pytz.timezone('Etc/GMT-3')
            datetime_Now = datetime.now(tz_IN)
            # We get a new frame from the webcam
            _, frame = cap.read()

            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)

            if (datetime_Now - endTime).days == 0:
                # print("EXAM OVER")
                break
            if ExitButtonState:
                break

    def checkEyeGaze(self, gaze, endTime, studentID, examID, startTime):
        resultEyeGazeCount = db.child("examEnroll").child(examID).child(studentID).child(
            "EyeGaze").get()
        prevcount = 0
        if resultEyeGazeCount.val() != None:
            for a in resultEyeGazeCount.val():
                prevcount += 1
        count = 1
        while True:
            tz_IN = pytz.timezone('Etc/GMT-3')
            datetime_Now = datetime.now(tz_IN)
            # success, image = webcam.read()
            try:
                left_pupil = gaze.pupil_left_coords()
                if str(left_pupil) is None or (str(left_pupil) is not None and not gaze.is_center()):
                    timeS = datetime.now(tz_IN)
                    while str(left_pupil) is None or (str(left_pupil) is not None and not gaze.is_center()):
                        timeE = datetime.now(tz_IN)
                        if (timeE - timeS).seconds > 10:
                            while str(left_pupil) is None or (str(left_pupil) is not None and not gaze.is_center()):
                                gaze.is_top()
                            timeD = datetime.now(tz_IN)
                            data1 = {"Alert": str(count + prevcount), "Duration": str((timeD - timeS).seconds),
                                     "Started": str(timeS - startTime), "Ended": str(timeD - startTime)}
                            # data1 = {"Alert": str(count), "Time": str((timeD - timeS).seconds), "Started": str(
                            # timeS.time()), "Ended": str(timeD.time())}
                            db.child("examEnroll").child(examID).child(studentID).child("EyeGaze").child(
                                "EG-" + str(count + prevcount)).set(data1)
                            # print("Alert " + str(count + prevcount) + " took " + str((timeD - timeS).seconds) + " seconds")
                            # print("Started: " + str(timeS.time()) + " Ended: " + str(timeD.time()))
                            count += 1
                            # parent = Path(__file__).parent
                            # registerPic = Path(parent, 'Temp', 'TempAttImg.png').__str__()
                            # cv2.imwrite(registerPic, image)
                            break
            except:
                continue

            if (datetime_Now - endTime).days == 0:
                # print("EXAM OVER")
                break
            if ExitButtonState:
                break


# MAIN METHOD


if __name__ == "__main__":
    app = FaceNet()
    app.geometry("1050x600")
    app.resizable(False, False)
    app.title("FaceNet")
    # app.iconbitmap('images/faceprint.jgp') It must end with .ico
    # root.geometry("1100x700")
    app.mainloop()
