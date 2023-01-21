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

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Knihovníci",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # LOGIN FRAME

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Login",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.login_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        # REGISTER FRAME

        self.register_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Register",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.register_button_event)
        self.register_button.grid(row=2, column=0, sticky="ew")

        # self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
        #                                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
        #                                               image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        # self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                                values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

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

        # TEXT EDIT
        self.entry = customtkinter.CTkEntry(self.home_frame, placeholder_text="CTkEntry")
        self.entry.grid(row=2, column=1, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.register_button.configure(fg_color=("gray75", "gray25") if name == "register" else "transparent")
        # self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "register":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")
        mongo_client = get_mongo_client()
        login_result = login(mongo_client, "login_lib", "lib_12345")
        if login_result[0]:
            user = login_result[1]
            if user.role == Roles.Librarian.name:
                current_user = Librarian(user)
                current_user = current_user.user.login_name
                print("User: " + current_user)
            # current_user = Librarian(user)

    def register_button_event(self):
        self.select_frame_by_name("register")

    def frame_3_button_event(self):

        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()