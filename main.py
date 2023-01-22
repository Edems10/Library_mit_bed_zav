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

mongo_client = get_mongo_client()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("library.py")
        self.geometry("700x800")
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
        self.navigation_frame.grid_rowconfigure(10, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=" Library",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.login_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Login",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.login_image, anchor="w", command=self.login_button_event)
        self.login_button.grid(row=1, column=0, sticky="ew")

        self.register_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Registration",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.register_button_event)
        self.register_button.grid(row=2, column=0, sticky="ew")

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="About",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.login_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=3, column=0, sticky="ew")




        #navigation frame for logged user
        self.navigation_frame_logged = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame_logged.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame_logged.grid_rowconfigure(10, weight=1)

        self.navigation_frame_logged_label = customtkinter.CTkLabel(self.navigation_frame_logged, text=" Library",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_logged_label.grid(row=0, column=0, padx=20, pady=20)

        self.navigation_frame_logged_main_button = customtkinter.CTkButton(self.navigation_frame_logged, corner_radius=0, height=40,
                                                       border_spacing=10, text="Library 123",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.main_button_event)
        self.navigation_frame_logged_main_button.grid(row=1, column=0, sticky="ew")

        self.navigation_frame_logged_my_books_button = customtkinter.CTkButton(self.navigation_frame_logged,
                                                                           corner_radius=0, height=40,
                                                                           border_spacing=10, text="My books",
                                                                           fg_color="transparent",
                                                                           text_color=("gray10", "gray90"),
                                                                           hover_color=("gray70", "gray30"),
                                                                           image=self.register_image, anchor="w",
                                                                           command=self.main_button_event)
        self.navigation_frame_logged_my_books_button.grid(row=2, column=0, sticky="ew")

        self.navigation_frame_logged_admin_logout_button = customtkinter.CTkButton(self.navigation_frame_logged,
                                                                                   corner_radius=0, height=40,
                                                                                   border_spacing=10,
                                                                                   text="Log out",
                                                                                   fg_color="transparent",
                                                                                   text_color=("gray10", "gray90"),
                                                                                   hover_color=("gray70", "gray30"),
                                                                                   image=self.register_image,
                                                                                   anchor="w",
                                                                                   command=self.navigation_frame_logged_admin_logout_button_event)
        self.navigation_frame_logged_admin_logout_button.grid(row=3, column=0, sticky="ew")





        # navigation frame for admin
        self.navigation_frame_logged_admin = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame_logged_admin.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame_logged_admin.grid_rowconfigure(10, weight=1)

        self.navigation_frame_logged_admin_label = customtkinter.CTkLabel(self.navigation_frame_logged_admin, text=" Library",
                                                                    image=self.logo_image,
                                                                    compound="left",
                                                                    font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_logged_admin_label.grid(row=0, column=0, padx=20, pady=20)

        self.navigation_frame_logged_admin_main_button = customtkinter.CTkButton(self.navigation_frame_logged_admin, corner_radius=0, height=40,
                                                   border_spacing=10, text="Library admin",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.register_image, anchor="w",
                                                   command=self.main_button_event)

        self.navigation_frame_logged_admin_main_button.grid(row=1, column=0, sticky="ew")

        self.navigation_frame_logged_admin_add_author = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Add author",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_add_author_event)

        self.navigation_frame_logged_admin_add_author.grid(row=2, column=0, sticky="ew")

        self.navigation_frame_logged_admin_edit_author = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                corner_radius=0, height=40,
                                                                                border_spacing=10,
                                                                                text="Edit author",
                                                                                fg_color="transparent",
                                                                                text_color=("gray10", "gray90"),
                                                                                hover_color=("gray70", "gray30"),
                                                                                image=self.register_image, anchor="w",
                                                                                command=self.admin_button_edit_author_event)

        self.navigation_frame_logged_admin_edit_author.grid(row=3, column=0, sticky="ew")

        self.navigation_frame_logged_admin_add_book = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Add book",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.admin_button_add_book_event)

        self.navigation_frame_logged_admin_add_book.grid(row=4, column=0, sticky="ew")

        self.navigation_frame_logged_admin_edit_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Edit user",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_edit_user_event)

        self.navigation_frame_logged_admin_edit_user.grid(row=5, column=0, sticky="ew")

        self.navigation_frame_logged_admin_logout_button = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Log out",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.navigation_frame_logged_admin_logout_button_event)
        self.navigation_frame_logged_admin_logout_button.grid(row=6, column=0, sticky="ew")






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







        # register page frame
        self.registration_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.registration_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.registration_label_firstname = customtkinter.CTkLabel(self.registration_frame,
                                                                  text="First Name: ", width=30, height=25,
                                                                  corner_radius=7)
        self.registration_label_firstname.grid(row=0, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_firstname = customtkinter.CTkEntry(self.registration_frame,
                                                                  placeholder_text="Enter First Name",
                                                                  width=200, height=30, border_width=2,
                                                                  corner_radius=10)
        self.registration_entry_firstname.grid(row=0, column=1, padx=10, columnspan=2)

        self.registration_label_surname = customtkinter.CTkLabel(self.registration_frame,
                                                                   text="Surname: ", width=30, height=25,
                                                                   corner_radius=7)
        self.registration_label_surname.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_surname = customtkinter.CTkEntry(self.registration_frame,
                                                                   placeholder_text="Enter Surname",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.registration_entry_surname.grid(row=1, column=1, padx=10, columnspan=2)

        self.registration_label_pid = customtkinter.CTkLabel(self.registration_frame,
                                                                 text="PID: ", width=30, height=25,
                                                                 corner_radius=7)
        self.registration_label_pid.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_pid = customtkinter.CTkEntry(self.registration_frame,
                                                                 placeholder_text="Enter PID",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.registration_entry_pid.grid(row=2, column=1, padx=10, columnspan=2)

        self.registration_label_address = customtkinter.CTkLabel(self.registration_frame,
                                                             text="Address: ", width=30, height=25,
                                                             corner_radius=7)
        self.registration_label_address.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_address = customtkinter.CTkEntry(self.registration_frame,
                                                             placeholder_text="Enter Address",
                                                             width=200, height=30, border_width=2,
                                                             corner_radius=10)
        self.registration_entry_address.grid(row=3, column=1, padx=10, columnspan=2)

        self.registration_label_username = customtkinter.CTkLabel(self.registration_frame,
                                                           text="Username: ", width=30, height=25, corner_radius=7)
        self.registration_label_username.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_username = customtkinter.CTkEntry(self.registration_frame, placeholder_text="Enter Username",
                                                           width=200, height=30, border_width=2, corner_radius=10)
        self.registration_entry_username.grid(row=4, column=1, padx=10, columnspan=2)

        self.registration_label_password = customtkinter.CTkLabel(self.registration_frame, text="Password: ", width=30, height=25,
                                                           corner_radius=7)
        self.registration_label_password.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.registration_entry_password = customtkinter.CTkEntry(self.registration_frame,
                                                           placeholder_text="Enter Password", width=200, height=30,
                                                           border_width=2, corner_radius=10, show="•")
        self.registration_entry_password.grid(row=5, column=1, padx=10, columnspan=2, pady=20)

        self.registration_button_register = customtkinter.CTkButton(self.registration_frame,
                                                          text="Register", width=70, fg_color="#36719F",
                                                          hover_color="#3B8ED0", text_color="#FFF",
                                                          command=self.register_button_register_user)
        self.registration_button_register.grid(row=6, column=0, padx=0, sticky='e')





        # admin add author frame
        self.admin_add_author_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_add_author_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_add_author_label_firstname = customtkinter.CTkLabel(self.admin_add_author_frame,
                                                           text="First name: ", width=30, height=25, corner_radius=7)
        self.admin_add_author_label_firstname.grid(row=0, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_author_entry_firstname = customtkinter.CTkEntry(self.admin_add_author_frame, placeholder_text="Enter First name",
                                                           width=200, height=30, border_width=2, corner_radius=10)
        self.admin_add_author_entry_firstname.grid(row=0, column=1, padx=10, columnspan=2)

        self.admin_add_author_label_surname = customtkinter.CTkLabel(self.admin_add_author_frame, text="Surname: ", width=30, height=25,
                                                           corner_radius=7)
        self.admin_add_author_label_surname.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_author_entry_surname = customtkinter.CTkEntry(self.admin_add_author_frame,
                                                           placeholder_text="Enter Surname", width=200, height=30,
                                                           border_width=2, corner_radius=10)
        self.admin_add_author_entry_surname.grid(row=1, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_author_button_add = customtkinter.CTkButton(self.admin_add_author_frame,
                                                          text="Add", width=70, fg_color="#36719F",
                                                          hover_color="#3B8ED0", text_color="#FFF",
                                                          command=self.admin_button_add_author)
        self.admin_add_author_button_add.grid(row=2, column=0, padx=0, sticky='e')




        # admin edit author frame

        self.admin_edit_author_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_edit_author_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_edit_author_label_ID = customtkinter.CTkLabel(self.admin_edit_author_frame,
                                                                        text="Author ID: ", width=30, height=25,
                                                                        corner_radius=7)
        self.admin_edit_author_label_ID.grid(row=0, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_author_entry_ID = customtkinter.CTkEntry(self.admin_edit_author_frame,
                                                                        placeholder_text="Enter Author ID",
                                                                        width=200, height=30, border_width=2,
                                                                        corner_radius=10)
        self.admin_edit_author_entry_ID.grid(row=0, column=1, padx=10, columnspan=2)

        self.admin_edit_author_label_firstname = customtkinter.CTkLabel(self.admin_edit_author_frame,
                                                                       text="First name: ", width=30, height=25,
                                                                       corner_radius=7)
        self.admin_edit_author_label_firstname.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_author_entry_firstname = customtkinter.CTkEntry(self.admin_edit_author_frame,
                                                                       placeholder_text="Enter First name",
                                                                       width=200, height=30, border_width=2,
                                                                       corner_radius=10)
        self.admin_edit_author_entry_firstname.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_edit_author_label_surname = customtkinter.CTkLabel(self.admin_edit_author_frame, text="Surname: ",
                                                                     width=30, height=25,
                                                                     corner_radius=7)
        self.admin_edit_author_label_surname.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_author_entry_surname = customtkinter.CTkEntry(self.admin_edit_author_frame,
                                                                     placeholder_text="Enter Surname", width=200,
                                                                     height=30,
                                                                     border_width=2, corner_radius=10)
        self.admin_edit_author_entry_surname.grid(row=2, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_author_button_edit = customtkinter.CTkButton(self.admin_edit_author_frame,
                                                                   text="Edit", width=70, fg_color="#36719F",
                                                                   hover_color="#3B8ED0", text_color="#FFF",
                                                                   command=self.admin_button_add_author)
        self.admin_edit_author_button_edit.grid(row=3, column=0, padx=0, sticky='e')





        # admin add book frame
        self.admin_add_book_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_add_book_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")


        self.admin_add_book_label_title = customtkinter.CTkLabel(self.admin_add_book_frame,
                                                                       text="Title: ", width=30, height=25,
                                                                       corner_radius=7)
        self.admin_add_book_label_title.grid(row=0, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_title = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                       placeholder_text="Enter Title",
                                                                       width=200, height=30, border_width=2,
                                                                       corner_radius=10)
        self.admin_add_book_entry_title.grid(row=0, column=1, padx=10, columnspan=2)

        self.admin_add_book_label_author = customtkinter.CTkLabel(self.admin_add_book_frame, text="Author ID: ",
                                                                     width=30, height=25,
                                                                     corner_radius=7)
        self.admin_add_book_label_author.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_author = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                     placeholder_text="Enter Author ID", width=200,
                                                                     height=30,
                                                                     border_width=2, corner_radius=10)
        self.admin_add_book_entry_author.grid(row=1, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_length = customtkinter.CTkLabel(self.admin_add_book_frame, text="Length: ",
                                                                    width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_book_label_length.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_length = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                    placeholder_text="Enter Length", width=200,
                                                                    height=30,
                                                                    border_width=2, corner_radius=10)
        self.admin_add_book_entry_length.grid(row=2, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_year = customtkinter.CTkLabel(self.admin_add_book_frame, text="Year: ",
                                                                    width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_book_label_year.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_year = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                    placeholder_text="Enter Year", width=200,
                                                                    height=30,
                                                                    border_width=2, corner_radius=10)
        self.admin_add_book_entry_year.grid(row=3, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_image = customtkinter.CTkLabel(self.admin_add_book_frame, text="Image: ",
                                                                    width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_book_label_image.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_image = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                    placeholder_text="Enter Image", width=200,
                                                                    height=30,
                                                                    border_width=2, corner_radius=10)
        self.admin_add_book_entry_image.grid(row=4, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_copies_available = customtkinter.CTkLabel(self.admin_add_book_frame, text="Copies available: ",
                                                                  width=30, height=25,
                                                                  corner_radius=7)
        self.admin_add_book_label_copies_available.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_copies_available = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                  placeholder_text="Enter Copies available", width=200,
                                                                  height=30,
                                                                  border_width=2, corner_radius=10)
        self.admin_add_book_entry_copies_available.grid(row=5, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_genre = customtkinter.CTkLabel(self.admin_add_book_frame, text="Genre: ",
                                                                   width=30, height=25,
                                                                   corner_radius=7)
        self.admin_add_book_label_genre.grid(row=6, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_genre = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                   placeholder_text="Enter Genre", width=200,
                                                                   height=30,
                                                                   border_width=2, corner_radius=10)
        self.admin_add_book_entry_genre.grid(row=6, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_description = customtkinter.CTkLabel(self.admin_add_book_frame,
                                                                              text="Description: ",
                                                                              width=30, height=25,
                                                                              corner_radius=7)
        self.admin_add_book_label_description.grid(row=7, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_description = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                              placeholder_text="Enter Description",
                                                                              width=200,
                                                                              height=30,
                                                                              border_width=2, corner_radius=10)
        self.admin_add_book_entry_description.grid(row=7, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_count_borrowed = customtkinter.CTkLabel(self.admin_add_book_frame,
                                                                         text="Count borrowed: ",
                                                                         width=30, height=25,
                                                                         corner_radius=7)
        self.admin_add_book_label_count_borrowed.grid(row=8, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_count_borrowed = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                         placeholder_text="Enter Count borrowed",
                                                                         width=200,
                                                                         height=30,
                                                                         border_width=2, corner_radius=10)
        self.admin_add_book_entry_count_borrowed.grid(row=8, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_button_add = customtkinter.CTkButton(self.admin_add_book_frame,
                                                                   text="Add", width=70, fg_color="#36719F",
                                                                   hover_color="#3B8ED0", text_color="#FFF",
                                                                   command=self.admin_button_add_book)
        self.admin_add_book_button_add.grid(row=9, column=0, padx=0, sticky='e')




        # admin edit user page frame
        self.admin_edit_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_edit_user_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_edit_user_label_id = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                      text="User ID: ", width=30, height=25,
                                                                      corner_radius=7)
        self.admin_edit_user_label_id.grid(row=0, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_id = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                      placeholder_text="Enter User ID",
                                                                      width=200, height=30, border_width=2,
                                                                      corner_radius=10)
        self.admin_edit_user_entry_id.grid(row=0, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_firstname = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                   text="First Name: ", width=30, height=25,
                                                                   corner_radius=7)
        self.admin_edit_user_label_firstname.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_firstname = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                   placeholder_text="Enter First Name",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.admin_edit_user_entry_firstname.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_surname = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                 text="Surname: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_user_label_surname.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_surname = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                 placeholder_text="Enter Surname",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_edit_user_entry_surname.grid(row=2, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_pid = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                             text="PID: ", width=30, height=25,
                                                             corner_radius=7)
        self.admin_edit_user_label_pid.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_pid = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                             placeholder_text="Enter PID",
                                                             width=200, height=30, border_width=2,
                                                             corner_radius=10)
        self.admin_edit_user_entry_pid.grid(row=3, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_address = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                 text="Address: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_user_label_address.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_address = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                 placeholder_text="Enter Address",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_edit_user_entry_address.grid(row=4, column=1, padx=10, columnspan=2)

        self.admin_edit_user_button_edit = customtkinter.CTkButton(self.admin_edit_user_frame,
                                                                    text="Edit", width=70, fg_color="#36719F",
                                                                    hover_color="#3B8ED0", text_color="#FFF",
                                                                    command=self.admin_button_edit_user)
        self.admin_edit_user_button_edit.grid(row=5, column=0, padx=0, sticky='e')




        #create main page after for normal user which logged sucessfully
        self.main_page_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_page_frame.grid_columnconfigure(0, weight=1)

        self.main_page_frame_label = customtkinter.CTkLabel(self.main_page_frame, text="User is logged")
        self.main_page_frame_label.grid(row=0, column=0, padx=20, pady=10)






        # create main page after for admin which logged sucessfully
        self.main_page_frame_admin = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_page_frame_admin.grid_columnconfigure(0, weight=1)

        self.main_page_frame_admin_label = customtkinter.CTkLabel(self.main_page_frame_admin, text="User is logged")
        self.main_page_frame_admin_label.grid(row=0, column=0, padx=20, pady=10)





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
        self.navigation_frame_logged_main_button.configure(fg_color=("gray75", "gray25") if name == "main" else "transparent")
        self.navigation_frame_logged_admin_main_button.configure(fg_color=("gray75", "gray25") if name == "main_admin" else "transparent")
        self.admin_add_author_button_add.configure(fg_color=("gray75", "gray25") if name == "add_author_admin" else "transparent")
        self.admin_edit_author_button_edit.configure(fg_color=("gray75", "gray25") if name == "edit_author_admin" else "transparent")
        self.admin_add_book_button_add.configure(fg_color=("gray75", "gray25") if name == "add_book_admin" else "transparent")
        self.admin_edit_user_button_edit.configure(fg_color=("gray75", "gray25") if name == "edit_user_admin" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
        else:
            self.home_frame.grid_forget()

        if name == "login":
            self.login_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
        else:
            self.login_frame.grid_forget()

        if name == "register":
            self.registration_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
        else:
            self.registration_frame.grid_forget()

        if name == "main":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
            self.navigation_frame_logged.grid(row=0, column=0, sticky="nsew")
            self.main_page_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.main_page_frame.grid_forget()

        if name == "main_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.navigation_frame_logged_admin.grid(row=0, column=0, sticky="nsew")
            self.main_page_frame_admin.grid(row=0, column=1, sticky="nsew")
        else:
            self.main_page_frame_admin.grid_forget()

        if name == "add_author_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_add_author_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_add_author_frame.grid_forget()

        if name == "edit_author_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_edit_author_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_edit_author_frame.grid_forget()

        if name == "add_book_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_add_book_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_add_book_frame.grid_forget()

        if name == "edit_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_edit_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_edit_user_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def login_button_event(self):
        self.select_frame_by_name("login")



    def login_button_log_user(self):
        mongo_client = get_mongo_client()
        username = self.login_entry_username.get()
        password = self.login_entry_password.get()
        #Admin: login_lib lib_12345
        #User: Dom2 password
        login_result = login(mongo_client, "login_lib", "lib_12345")
        if login_result[0]:
            user = login_result[1]
            global current
            current = login_result[1]
            if user.role == Roles.Librarian.name:
                current_user = Librarian(user)
                self.select_frame_by_name("main_admin")
                self.main_page_frame_admin_label.configure(text="Admin: " + current_user.user.login_name + " is logged")
                self.navigation_frame_logged_admin_label.configure(text=" Admin")
            else:
                current_user = User(user)
                self.select_frame_by_name("main")
                self.main_page_frame_label.configure(text="User: " + current_user.user.login_name + " is logged")
                self.navigation_frame_logged_label.configure(text=" " + current_user.user.login_name)
        else:
            print(login_result[1])

    def admin_button_add_author_event(self):
        self.select_frame_by_name("add_author_admin")

    def admin_button_add_author(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            firstname = self.admin_add_author_entry_firstname.get()
            surname = self.admin_add_author_entry_surname.get()
            added_author = current_user.add_author(mongo_client, firstname, surname)
            if added_author[0] == True:
                self.select_frame_by_name("main_admin")
                print(added_author[0])
            else:
                print(added_author[1])
                self.select_frame_by_name("add_author_admin")

    def admin_button_edit_author_event(self):
        self.select_frame_by_name("edit_author_admin")

    def admin_button_edit_author(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            firstname = self.admin_add_author_entry_firstname.get()
            surname = self.admin_add_author_entry_surname.get()
            added_author = current_user.add_author(mongo_client, firstname, surname)
            if added_author[0] == True:
                self.select_frame_by_name("main_admin")
                print(added_author[0])
            else:
                print(added_author[1])
                self.select_frame_by_name("edit_author_admin")

    def admin_button_add_book_event(self):
        self.select_frame_by_name("add_book_admin")

    def admin_button_add_book(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            title = self.admin_add_book_entry_title.get()
            author = self.admin_add_book_entry_author.get()
            length = self.admin_add_book_entry_length.get()
            year = self.admin_add_book_entry_year.get()
            image = self.admin_add_book_entry_image.get()
            copies_available = self.admin_add_book_entry_copies_available.get()
            genre = self.admin_add_book_entry_genre.get()
            description = self.admin_add_book_entry_description.get()
            count_borrowed = self.admin_add_book_entry_count_borrowed.get()
            added_book = current_user.add_book(mongo_client, title, author, length, year, image, copies_available, genre, description, count_borrowed)
            if added_book[0] == True:
                self.select_frame_by_name("main_admin")
                print(added_book[0])
            else:
                print(added_book[1])
                self.select_frame_by_name("add_book_admin")

    def admin_button_edit_user_event(self):
        self.select_frame_by_name("edit_user_admin")

    def admin_button_edit_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_edit_user_entry_id.get()
            firstname = self.admin_edit_user_entry_firstname.get()
            surname = self.admin_edit_user_entry_surname.get()
            pid = self.admin_edit_user_entry_pid.get()
            address = self.admin_edit_user_entry_address.get()
            edited_user = current_user.edit_user(mongo_client, firstname, surname, pid, address, _id = id)
            if edited_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(edited_user[0])
            else:
                print(edited_user[1])
                self.select_frame_by_name("edit_user_admin")
    def show_next_book_user(self):
        print("next book")

    def register_button_event(self):
        self.select_frame_by_name("register")

    def register_button_register_user(self):
        mongo_client = get_mongo_client()
        firstname = self.registration_entry_firstname.get()
        surname = self.registration_entry_surname.get()
        pid = self.registration_entry_pid.get()
        address = self.registration_entry_address.get()
        username = self.registration_entry_username.get()
        password = self.registration_entry_password.get()
        registration_result = create_account(mongo_client, firstname, surname, pid, address, username, password)
        register_user = registration_result[0]
        if register_user == True:
            self.select_frame_by_name("login")
            print(registration_result[0])
        else:
            print(registration_result[1])

    def main_button_event(self):
        self.select_frame_by_name("register")


    def navigation_frame_logged_admin_logout_button_event(self):
        self.select_frame_by_name("login")
        self.login_entry_username.delete(0, "end")
        self.login_entry_password.delete(0, "end")


#    def ChangeLabelMainPageText(m):
#        m.configure(text='You pressed the button!')

if __name__ == "__main__":
    app = App()
    app.mainloop()