import tkinter

import customtkinter
import os
from PIL import Image

import pymongo
import os
from bson.objectid import ObjectId
from torch import true_divide
from actions import *
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from datamodels import Autocomplete_options_book, Autocomplete_options_user, Person, Roles

API_KEY = os.path.join(os.path.dirname(__file__), 'api_key.env')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'Book_img')


def get_mongo_client():
    with open(API_KEY) as f:
        secret = f.read()
    return pymongo.MongoClient(secret)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("title.py")
        self.geometry("700x450")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Icons")
        # main image on top left
        self.logo_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "icons8-library-building-100.png")), size=(26, 26))
        # center image
        self.large_test_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "library-book-svgrepo-com.png")), size=(500, 150))
        # icon image
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Logo.png")), size=(20, 20))

        self.login_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "icons8-login-rounded-90.png")),
            dark_image=Image.open(os.path.join(image_path, "icons8-login-rounded-90.png")), size=(20, 20))

        self.register_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "icons8-sign-up-64.png")),
            dark_image=Image.open(os.path.join(image_path, "icons8-sign-up-64.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "Logo.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "Logo.png")),
                                                     size=(20, 20))







        # navigation frame for not logged user
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Knihovníci",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.login_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.login_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Login",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.login_image, anchor="w", command=self.login_button_event)
        self.login_button.grid(row=2, column=0, sticky="ew")

        self.register_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Register",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.register_button_event)
        self.register_button.grid(row=3, column=0, sticky="ew")




        #navigation frame for logged user
        self.navigation_frame_logged = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame_logged.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame_logged.grid_rowconfigure(4, weight=1)

        self.navigation_frame_logged_label = customtkinter.CTkLabel(self.navigation_frame_logged, text=" Knihovníci",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_logged_label.grid(row=0, column=0, padx=20, pady=20)

        self.main_button = customtkinter.CTkButton(self.navigation_frame_logged, corner_radius=0, height=40,
                                                       border_spacing=10, text="Library",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.main_button_event)
        self.main_button.grid(row=3, column=0, sticky="ew")






        #login page frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.login_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.login_label_username = customtkinter.CTkLabel(self.login_frame,
                                                           text="Username: ", width=30, height=25, corner_radius=7)
        self.login_label_username.grid(row=0, column=0, padx=10, pady=20,  sticky='e')

        self.login_entry_username = customtkinter.CTkEntry(self.login_frame, placeholder_text="Enter Username", width=200, height=30, border_width=2, corner_radius=10)
        self.login_entry_username.grid(row=0, column=1, padx=10, columnspan=2)

        # Label Password
        self.login_label_password = customtkinter.CTkLabel(self.login_frame, text="Password: ", width=30, height=25, corner_radius=7)
        self.login_label_password.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        # Entry Password
        self.login_entry_password = customtkinter.CTkEntry(self.login_frame,
                                                           placeholder_text="Enter Password", width=200, height=30,
                                                           border_width=2, corner_radius=10, show="•")
        self.login_entry_password.grid(row=1, column=1, padx=10, columnspan=2, pady=20)

        # Button Login
        self.login_button_login = customtkinter.CTkButton(self.login_frame,
                                                          text="Login", width=70, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.login_button_log_user)
        self.login_button_login.grid(row=2, column=0, padx=0, sticky='e')




        #create main page after user is logged sucessfully
        self.main_page_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_page_frame.grid_columnconfigure(0, weight=1)

        self.main_page_frame_label = customtkinter.CTkLabel(self.main_page_frame, text="User is logged")
        self.main_page_frame_label.grid(row=0, column=0, padx=20, pady=10)





        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="",
                                                                   image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="", image=self.image_icon_image)
        self.home_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="CTkButton",
                                                           image=self.image_icon_image, compound="right")
        self.home_frame_button_2.grid(row=2, column=0, padx=20, pady=10)



        # select default frame
        self.select_frame_by_name("login")

    def select_frame_by_name(self, name):
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.login_button.configure(fg_color=("gray75", "gray25") if name == "login" else "transparent")
        self.register_button.configure(fg_color=("gray75", "gray25") if name == "register" else "transparent")
        self.main_button.configure(fg_color=("gray75", "gray25") if name == "main" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
        else:
            self.home_frame.grid_forget()
        if name == "login":
            self.login_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
        else:
            self.login_frame.grid_forget()
        if name == "register":
            self.navigation_frame_logged.grid_forget()

        if name == "main":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid(row=0, column=0, sticky="nsew")
            self.main_page_frame.grid(row=0, column=1, sticky="nsew")
        else:

            self.main_page_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def login_button_event(self):
        self.select_frame_by_name("login")

    def login_button_log_user(self):
        mongo_client = get_mongo_client()
        username = self.login_entry_username.get()
        password = self.login_entry_password.get()
        #Dom2 password
        login_result = login(mongo_client, username, password)
        if login_result[0]:
            user = login_result[1]
            if user.role == Roles.Librarian.name:
                current_user = Librarian(user)
                print("User: " + current_user.user.login_name)
                self.select_frame_by_name("main")
            else:
                current_user = User(user)
                print("User: " + current_user.user.login_name)
                self.select_frame_by_name("main")
        else:
            print(login_result[1])


    def register_button_event(self):
        self.select_frame_by_name("register")

    def main_button_event(self):
        self.select_frame_by_name("register")

if __name__ == "__main__":
    app = App()
    app.mainloop()