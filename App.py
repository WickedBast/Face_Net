import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
import pyrebase
import cv2
from pathlib import Path
import face_recognition
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import webbrowser

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
admin = firebase_admin.initialize_app(cred, {"databaseURL": "https://facenet-f0615-default-rtdb.firebaseio.com/"})

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth1 = firebase.auth()
encodelist = ()


# root = Tk()
# root.geometry("1100x700")


class FaceNet(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Login, StudentRegister, TeacherRegister, ForgotPassword):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Login)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Login(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

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
                        print(auth1.sign_in_with_email_and_password(str(email.get()), str(password.get())))
                    else:
                        messagebox.showerror("Email Not Verified or Not Registered", "Please check your email")
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
            controller.show_frame(StudentRegister)

        def backT():
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            controller.show_frame(TeacherRegister)

        welcome = Label(self, text=" SIGN IN ", width=150, height=5)
        welcome.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

        emailL = Label(self, text="E-mail:", width=10, height=2)
        emailL.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        email.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Email")

        passwordL = Label(self, text="Password:", width=10, height=2)
        passwordL.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        password = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF", show="*")
        password.grid(row=7, column=1, columnspan=3, padx=10, pady=10)
        password.insert(0, "Password")

        refresh()

        forgotPassword = ttk.Button(self, text="Forgot your password?", cursor="hand2",
                                    command=lambda: controller.show_frame(ForgotPassword))
        forgotPassword.grid(row=23, column=1, columnspan=3, padx=10, pady=10)

        myButton = Button(self, text="Sign In!", command=login, fg="white", bg="orange")
        myButton.grid(row=17, column=1, columnspan=3, padx=10, pady=10)

        buttonStudent = ttk.Button(self, text="Student Sign Up", command=backS)
        buttonStudent.grid(row=21, column=0, columnspan=3, padx=5, pady=5)

        buttonTeacher = ttk.Button(self, text="Teacher Sign Up", command=backT)
        buttonTeacher.grid(row=21, column=2, columnspan=3, padx=5, pady=5)


class StudentRegister(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def register():
            if str(name.get()).isspace() or str(surname.get()).isspace() or str(email.get()).isspace() or str(
                    password.get()).isspace() or str(passwordA.get()).isspace() or str(studentID.get()).isspace():
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif len(str(name.get())) == 0 or len(str(surname.get())) == 0 or len(str(email.get())) == 0 \
                    or len(str(password.get())) == 0 or len(str(passwordA.get())) == 0 or len(
                str(studentID.get())) == 0:
                messagebox.showerror("Blank spaces", "Please fill the blank areas.")
            elif not str(name.get()).isalpha() or not str(surname.get()).isalpha():
                messagebox.showerror("Wrong Input", "Your name or surname typed wrong.")
            elif len(str(studentID.get())) != 9:
                messagebox.showerror("Wrong ID", "Your ID is incorrect.")
            elif not str(email.get()).endswith("@isik.edu.tr"):
                messagebox.showerror("Wrong Email", "Please enter your Işık University Email.")
            elif len(str(password.get())) < 6:
                messagebox.showwarning("Short Password", "Your password is shorter than 6 characters.")
            elif len(str(password.get())) > 16:
                messagebox.showwarning("Short Password", "Your password is longer than 16 characters.")
            elif str(password.get()) != str(passwordA.get()):
                messagebox.showerror("Password Mismatch", "Your passwords do not match.")
            elif not len(db.child("students").order_by_child("id").equal_to(str(studentID.get())).get().val()) == 0:
                messagebox.showerror("ID Already Exists", "This ID is registered to the system.")
            else:
                try:
                    auth1.create_user_with_email_and_password(str(email.get()), str(password.get()))
                except:
                    messagebox.showerror("Email Already Exists", "This email is registered to the system.")
                    return
                print(str(name.get()), str(surname.get()), str(studentID.get()), str(email.get()), str(password.get()))
                encoding = takePhoto()
                registerStudent(str(name.get()), str(surname.get()), str(studentID.get()), str(email.get()), encoding,
                                str(password.get()))
                login = auth1.sign_in_with_email_and_password(str(email.get()), str(password.get()))
                auth1.send_email_verification(login["idToken"])
                messagebox.showinfo("User Created", "Check your email to complete registration.")
                controller.show_frame(Login)

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
                print(encode)
                encodeList.append(encode)
            return encodeList

        def takePhoto():
            cam = cv2.VideoCapture(0)
            cv2.namedWindow("test")
            while True:
                ret, frame = cam.read()
                if not ret:
                    print("failed to grab frame")
                    break
                cv2.imshow("test", frame)

                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    break
                elif k % 256 == 32:
                    # SPACE pressed

                    parent = Path(__file__).parent
                    print(parent)
                    registerPic = Path(parent, 'Temp', 'TEST.png').__str__()
                    print(registerPic)
                    cv2.imwrite(registerPic, frame)
                    myList = os.listdir('Temp')
                    print(myList)
                    images = []
                    for cl in myList:
                        x = Path(parent, 'Temp')
                        curImg = cv2.imread(f'{x}/{cl}')
                        images.append(curImg)
                    print(images)
                    encodelist = findEncodings(images)

            cam.release()

            cv2.destroyAllWindows()
            return list(encodelist[0])

        def refresh():
            name.bind("<FocusIn>", lambda args: name.delete(0, 'end'))
            surname.bind("<FocusIn>", lambda args: surname.delete(0, 'end'))
            studentID.bind("<FocusIn>", lambda args: studentID.delete(0, 'end'))
            email.bind("<FocusIn>", lambda args: email.delete(0, 'end'))
            password.bind("<FocusIn>", lambda args: password.delete(0, 'end'))
            passwordA.bind("<FocusIn>", lambda args: passwordA.delete(0, 'end'))

        def back():
            name.delete(0, 'end')
            name.insert(0, "Name")
            surname.delete(0, 'end')
            surname.insert(0, "Surname")
            studentID.delete(0, 'end')
            studentID.insert(0, "Student ID")
            email.delete(0, 'end')
            email.insert(0, "Email")
            password.delete(0, 'end')
            password.insert(0, "Password")
            passwordA.delete(0, 'end')
            passwordA.insert(0, "Password")
            controller.show_frame(Login)

        welcome = Label(self, text=" STUDENT SIGN UP ", width=150, height=5)
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        name = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        name.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        name.insert(0, "Name")

        surname = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        surname.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        surname.insert(0, "Surname")

        studentID = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        studentID.grid(row=7, column=1, columnspan=3, padx=10, pady=10)
        studentID.insert(0, "Student ID")

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

        myButton = Button(self, text="Sign Up!", command=register, fg="white", bg="orange")
        myButton.grid(row=15, column=1, columnspan=3, padx=10, pady=10)

        buttonBack = ttk.Button(self, text="Back", command=back)
        buttonBack.grid(row=15, column=0, columnspan=3, padx=5, pady=5)


class TeacherRegister(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

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
                print(str(name.get()), str(surname.get()), str(email.get()), str(password.get()))
                registerTeacher(str(name.get()), str(surname.get()), str(email.get()), str(password.get()))
                login = auth1.sign_in_with_email_and_password(str(email.get()), str(password.get()))
                auth1.send_email_verification(login["idToken"])
                messagebox.showinfo("User Created", "Check your email to complete registration.")
                controller.show_frame(Login)

        def registerTeacher(name, surname, email, password):
            data1 = {"name": name, "surname": surname, "email": email}
            croppedEmail = email[:-14]
            croppedEmail = croppedEmail.replace(".", "")
            print(croppedEmail)
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

        welcome = Label(self, text=" TEACHER SIGN UP ", width=150, height=5)
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

        myButton = Button(self, text="Sign Up!", command=register, fg="white", bg="orange")
        myButton.grid(row=15, column=1, columnspan=3, padx=10, pady=10)

        buttonBack = ttk.Button(self, text="Back", command=back)
        buttonBack.grid(row=15, column=0, columnspan=3, padx=5, pady=5)


class ForgotPassword(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

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

        welcome = Label(self, text=" FORGOT PASSWORD ", width=150, height=5)
        welcome.grid(row=1, column=1, columnspan=3, padx=10, pady=10)

        email = Entry(self, width=50, borderwidth=5, bg="#72A4D2", fg="#FFFFFF")
        email.grid(row=3, column=1, columnspan=3, padx=10, pady=10)
        email.insert(0, "Enter your email")

        refresh()

        buttonBack = ttk.Button(self, text="Back", command=back)
        buttonBack.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        myButton = Button(self, text="Submit", command=mail, fg="white", bg="orange")
        myButton.grid(row=5, column=1, columnspan=3, padx=10, pady=10)


app = FaceNet()
app.mainloop()
