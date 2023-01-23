from ast import List
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

IMAGES_DIR = os.path.join(os.path.dirname(__file__),'Book_img')


API_KEY = os.path.join(os.path.dirname(__file__), 'api_key.env')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'Book_img')

CURRENT_SELECTED_BOOK_MAIN_PAGE = 0
CURRENT_USER_SELECTED_MY_BOOK = 0
ALL_LIBRARY_BOOKS = None
CURRENT_USER = None
CURRENT_USER_BORROWED_BOOKS = None
PATH_TO_LOCAL_IMAGES_BOOKS = os.path.join(os.path.dirname(__file__), 'book_images')


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

        # WITCHER IMAGE TEST
        self.book_test_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "book.jpg")), size=(200, 300))
        
        self.no_book_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "placeholder_no_book.png")), size=(200, 300))
        
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

        self.navigation_frame_logged_label = customtkinter.CTkLabel(self.navigation_frame_logged, text="Library",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_logged_label.grid(row=0, column=0, padx=20, pady=20)

        self.navigation_frame_logged_main_button = customtkinter.CTkButton(self.navigation_frame_logged, corner_radius=0, height=40,
                                                       border_spacing=10, text="Your Library",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=self.register_image, anchor="w",
                                                       command=self.navigation_frame_logged_main_page_event)
        self.navigation_frame_logged_main_button.grid(row=1, column=0, sticky="ew")

        self.navigation_frame_logged_my_books_button = customtkinter.CTkButton(self.navigation_frame_logged,
                                                                           corner_radius=0, height=40,
                                                                           border_spacing=10, text="My books",
                                                                           fg_color="transparent",
                                                                           text_color=("gray10", "gray90"),
                                                                           hover_color=("gray70", "gray30"),
                                                                           image=self.register_image, anchor="w",
                                                                           command=self.navigation_frame_logged_my_books_button_event)
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
        self.navigation_frame_logged_admin.grid_rowconfigure(15, weight=1)

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
                                                   command=self.navigation_frame_admin_main_page_event)

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

        self.navigation_frame_logged_admin_delete_author = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Delete author",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.admin_button_delete_author_event)

        self.navigation_frame_logged_admin_delete_author.grid(row=4, column=0, sticky="ew")

        self.navigation_frame_logged_admin_add_book = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Add book",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.admin_button_add_book_event)

        self.navigation_frame_logged_admin_add_book.grid(row=5, column=0, sticky="ew")

        self.navigation_frame_logged_admin_edit_book = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                              corner_radius=0, height=40,
                                                                              border_spacing=10,
                                                                              text="Edit book",
                                                                              fg_color="transparent",
                                                                              text_color=("gray10", "gray90"),
                                                                              hover_color=("gray70", "gray30"),
                                                                              image=self.register_image, anchor="w",
                                                                              command=self.admin_button_edit_book_event)

        self.navigation_frame_logged_admin_edit_book.grid(row=6, column=0, sticky="ew")

        self.navigation_frame_logged_admin_delete_book = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Delete book",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_delete_book_event)

        self.navigation_frame_logged_admin_delete_book.grid(row=7, column=0, sticky="ew")

        self.navigation_frame_logged_admin_add_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Add user",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_add_user_event)

        self.navigation_frame_logged_admin_add_user.grid(row=8, column=0, sticky="ew")

        self.navigation_frame_logged_admin_edit_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Edit user",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_edit_user_event)

        self.navigation_frame_logged_admin_edit_user.grid(row=9, column=0, sticky="ew")

        self.navigation_frame_logged_admin_delete_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                               corner_radius=0, height=40,
                                                                               border_spacing=10,
                                                                               text="Delete user",
                                                                               fg_color="transparent",
                                                                               text_color=("gray10", "gray90"),
                                                                               hover_color=("gray70", "gray30"),
                                                                               image=self.register_image, anchor="w",
                                                                               command=self.admin_button_delete_user_event)

        self.navigation_frame_logged_admin_delete_user.grid(row=10, column=0, sticky="ew")

        self.navigation_frame_logged_admin_ban_unban_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Ban / Unban",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.admin_button_ban_user_event)

        self.navigation_frame_logged_admin_ban_unban_user.grid(row=11, column=0, sticky="ew")

        self.navigation_frame_logged_admin_verified_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                    corner_radius=0, height=40,
                                                                                    border_spacing=10,
                                                                                    text="Verify / Unverify",
                                                                                    fg_color="transparent",
                                                                                    text_color=("gray10", "gray90"),
                                                                                    hover_color=("gray70", "gray30"),
                                                                                    image=self.register_image,
                                                                                    anchor="w",
                                                                                    command=self.admin_button_verified_user_event)

        self.navigation_frame_logged_admin_verified_user.grid(row=12, column=0, sticky="ew")

        self.navigation_frame_logged_admin_accept_changes_user = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                   corner_radius=0, height=40,
                                                                                   border_spacing=10,
                                                                                   text="Accept / decline",
                                                                                   fg_color="transparent",
                                                                                   text_color=("gray10", "gray90"),
                                                                                   hover_color=("gray70", "gray30"),
                                                                                   image=self.register_image,
                                                                                   anchor="w",
                                                                                   command=self.admin_button_accept_changes_user_event)

        self.navigation_frame_logged_admin_accept_changes_user.grid(row=13, column=0, sticky="ew")

        self.navigation_frame_logged_admin_logout_button = customtkinter.CTkButton(self.navigation_frame_logged_admin,
                                                                                 corner_radius=0, height=40,
                                                                                 border_spacing=10,
                                                                                 text="Log out",
                                                                                 fg_color="transparent",
                                                                                 text_color=("gray10", "gray90"),
                                                                                 hover_color=("gray70", "gray30"),
                                                                                 image=self.register_image, anchor="w",
                                                                                 command=self.navigation_frame_logged_admin_logout_button_event)
        self.navigation_frame_logged_admin_logout_button.grid(row=14, column=0, sticky="ew")




        #Main page LIBRARY page for logged in user

        
        self.main_page_logged_in_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_page_logged_in_user_frame.grid(row=1, column=2, sticky="nsew")
        
        self.book_image_main_page = customtkinter.CTkLabel(self.main_page_logged_in_user_frame, text="",
                                                           image=self.book_test_image, compound="right")
        self.book_image_main_page.grid(row=1, column=2, padx=0, pady=20,  sticky='e')
        
        self.next_boook_button_main_page = customtkinter.CTkButton(self.main_page_logged_in_user_frame,
                                                          text="Next book", width=200, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.show_next_book_main_page)
        self.next_boook_button_main_page.grid(row=2, column=2,padx=0)
        
        self.borrow_book_button_main_page = customtkinter.CTkButton(self.main_page_logged_in_user_frame,
                                                          text="Borrow book", width=200, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.borrow_book_user)
        self.borrow_book_button_main_page.grid(row=3, column=2, padx=0)
        
        
        self.book_title_main_page = customtkinter.CTkLabel(self.main_page_logged_in_user_frame, text="Title:", compound="right")
        self.book_title_main_page.grid(row=1, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_title_main_page = customtkinter.CTkTextbox(self.main_page_logged_in_user_frame, width=100,height=100)
        self.textbox_title_main_page.grid(row=1, column=4, padx=(20, 0), pady=(20, 0))
        
        self.book_author_main_page = customtkinter.CTkLabel(self.main_page_logged_in_user_frame, text="Author:", compound="right")
        self.book_author_main_page.grid(row=2, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_author_main_page = customtkinter.CTkTextbox(self.main_page_logged_in_user_frame, width=100,height=100)
        self.textbox_author_main_page.grid(row=2, column=4, padx=(20, 0), pady=(20, 0))
        
        self.book_description_main_page = customtkinter.CTkLabel(self.main_page_logged_in_user_frame, text="Description:", compound="right")
        self.book_description_main_page.grid(row=3, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_book_description_main_page = customtkinter.CTkTextbox(self.main_page_logged_in_user_frame, width=100,height=100)
        self.textbox_book_description_main_page.grid(row=3, column=4, padx=(20, 0), pady=(20, 0))
        
        
        
        
        
        

        #MY BOOKS page for logged in user
        self.my_book_loged_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.my_book_loged_user_frame.grid(row=3, column=2, sticky="nsew")
        
        self.book_image_my_books_page = customtkinter.CTkLabel(self.my_book_loged_user_frame, text="",
                                                           image=self.book_test_image, compound="right")
        self.book_image_my_books_page.grid(row=1, column=2, padx=0, pady=20,  sticky='e')
        
        self.next_boook_button_my_books_page = customtkinter.CTkButton(self.my_book_loged_user_frame,
                                                          text="Next borrowed book", width=200, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.show_next_book_my_page)
        self.next_boook_button_my_books_page.grid(row=2, column=2,padx=0)
        
        self.return_book_button_my_books_page = customtkinter.CTkButton(self.my_book_loged_user_frame,
                                                          text="Return Book", width=200, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.return_book_user)
        self.return_book_button_my_books_page.grid(row=3, column=2, padx=0)
        
        
        self.book_title_my_books_page= customtkinter.CTkLabel(self.my_book_loged_user_frame, text="Title:", compound="right")
        self.book_title_my_books_page.grid(row=1, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_title_my_books_page = customtkinter.CTkTextbox(self.my_book_loged_user_frame, width=100,height=100)
        self.textbox_title_my_books_page.grid(row=1, column=4, padx=(20, 0), pady=(20, 0))
        
        self.book_author_my_books_page = customtkinter.CTkLabel(self.my_book_loged_user_frame, text="Author:", compound="right")
        self.book_author_my_books_page.grid(row=2, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_author_my_books_page = customtkinter.CTkTextbox(self.my_book_loged_user_frame, width=100,height=100)
        self.textbox_author_my_books_page.grid(row=2, column=4, padx=(20, 0), pady=(20, 0))
        
        self.book_description_my_books_page = customtkinter.CTkLabel(self.my_book_loged_user_frame, text="Description:", compound="right")
        self.book_description_my_books_page.grid(row=3, column=3, padx=10, pady=20,  sticky='e')
        
        self.textbox_book_description_my_books_page = customtkinter.CTkTextbox(self.my_book_loged_user_frame, width=100,height=100)
        self.textbox_book_description_my_books_page.grid(row=3, column=4, padx=(20, 0), pady=(20, 0))


        #login page frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.login_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.login_label_username = customtkinter.CTkLabel(self.login_frame,
                                                           text="Username: ", width=30, height=25, corner_radius=7)
        self.login_label_username.grid(row=1, column=0, padx=10, pady=20,  sticky='e')

        self.login_entry_username = customtkinter.CTkEntry(self.login_frame, placeholder_text="Enter Username", width=200, height=30, border_width=2, corner_radius=10)
        self.login_entry_username.grid(row=1, column=1, padx=10, columnspan=2)

        self.login_label_password = customtkinter.CTkLabel(self.login_frame, text="Password: ", width=30, height=25, corner_radius=7)
        self.login_label_password.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.login_entry_password = customtkinter.CTkEntry(self.login_frame,
                                                           placeholder_text="Enter Password", width=200, height=30,
                                                           border_width=2, corner_radius=10, show="•")
        self.login_entry_password.grid(row=2, column=1, padx=10, columnspan=2, pady=20)

        self.login_button_login = customtkinter.CTkButton(self.login_frame,
                                                          text="Login", width=70, fg_color="#36719F", hover_color="#3B8ED0", text_color="#FFF", command=self.login_button_log_user)
        self.login_button_login.grid(row=3, column=1, padx=70, sticky='w')







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
                                                                   command=self.admin_button_edit_author)
        self.admin_edit_author_button_edit.grid(row=3, column=0, padx=0, sticky='e')





        # admin delete author frame
        self.admin_delete_author_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_delete_author_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_delete_author_label_delete = customtkinter.CTkLabel(self.admin_delete_author_frame,
                                                               text="Delete author", width=60, height=20,
                                                               corner_radius=7)
        self.admin_delete_author_label_delete.grid(row=0, column=1, padx=80, pady=20, sticky='w')

        self.admin_delete_author_label_ID = customtkinter.CTkLabel(self.admin_delete_author_frame,
                                                                 text="Author ID: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_delete_author_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_delete_author_entry_ID = customtkinter.CTkEntry(self.admin_delete_author_frame,
                                                                 placeholder_text="Enter Author ID",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_delete_author_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_delete_author_button_delete = customtkinter.CTkButton(self.admin_delete_author_frame,
                                                                     text="Delete", width=70, fg_color="#36719F",
                                                                     hover_color="#3B8ED0", text_color="#FFF",
                                                                     command=self.admin_button_delete_author)
        self.admin_delete_author_button_delete.grid(row=2, column=1, padx=85, sticky='w')





        # admin add book frame
        self.admin_add_book_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_add_book_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_add_book_label_add = customtkinter.CTkLabel(self.admin_add_book_frame,
                                                                 text="Add book", width=60, height=20,
                                                                 corner_radius=7)
        self.admin_add_book_label_add.grid(row=0, column=1, padx=80, pady=20, sticky='w')

        self.admin_add_book_label_title = customtkinter.CTkLabel(self.admin_add_book_frame,
                                                                       text="Title: ", width=30, height=25,
                                                                       corner_radius=7)
        self.admin_add_book_label_title.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_title = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                       placeholder_text="Enter Title",
                                                                       width=200, height=30, border_width=2,
                                                                       corner_radius=10)
        self.admin_add_book_entry_title.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_add_book_label_author = customtkinter.CTkLabel(self.admin_add_book_frame, text="Author ID: ",
                                                                     width=30, height=25,
                                                                     corner_radius=7)
        self.admin_add_book_label_author.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_author = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                     placeholder_text="Enter Author ID", width=200,
                                                                     height=30,
                                                                     border_width=2, corner_radius=10)
        self.admin_add_book_entry_author.grid(row=2, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_length = customtkinter.CTkLabel(self.admin_add_book_frame, text="Length: ",
                                                                    width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_book_label_length.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_length = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                    placeholder_text="Enter Length", width=200,
                                                                    height=30,
                                                                    border_width=2, corner_radius=10)
        self.admin_add_book_entry_length.grid(row=3, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_book_label_year = customtkinter.CTkLabel(self.admin_add_book_frame, text="Year: ",
                                                                    width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_book_label_year.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_book_entry_year = customtkinter.CTkEntry(self.admin_add_book_frame,
                                                                    placeholder_text="Enter Year", width=200,
                                                                    height=30,
                                                                    border_width=2, corner_radius=10)
        self.admin_add_book_entry_year.grid(row=4, column=1, padx=10, columnspan=2, pady=20)

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
        self.admin_add_book_button_add.grid(row=9, column=1, padx=60, pady=20, sticky='w')





        # admin edit book frame
        self.admin_edit_book_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_edit_book_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_edit_book_label_edit = customtkinter.CTkLabel(self.admin_edit_book_frame,
                                                                     text="Edit book", width=60, height=20,
                                                                     corner_radius=7)
        self.admin_edit_book_label_edit.grid(row=0, column=1, padx=80, pady=20, sticky='w')

        self.admin_edit_book_label_book_ID = customtkinter.CTkLabel(self.admin_edit_book_frame,
                                                                  text="Book ID: ", width=30, height=25,
                                                                  corner_radius=7)
        self.admin_edit_book_label_book_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_book_ID = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                  placeholder_text="Enter Book ID",
                                                                  width=200, height=30, border_width=2,
                                                                  corner_radius=10)
        self.admin_edit_book_entry_book_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_edit_book_label_title = customtkinter.CTkLabel(self.admin_edit_book_frame,
                                                                 text="Title: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_book_label_title.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_title = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                 placeholder_text="Enter Title",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_edit_book_entry_title.grid(row=2, column=1, padx=10, columnspan=2)

        self.admin_edit_book_label_author = customtkinter.CTkLabel(self.admin_edit_book_frame, text="Author ID: ",
                                                                  width=30, height=25,
                                                                  corner_radius=7)
        self.admin_edit_book_label_author.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_author = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                  placeholder_text="Enter Author ID", width=200,
                                                                  height=30,
                                                                  border_width=2, corner_radius=10)
        self.admin_edit_book_entry_author.grid(row=3, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_label_length = customtkinter.CTkLabel(self.admin_edit_book_frame, text="Length: ",
                                                                  width=30, height=25,
                                                                  corner_radius=7)
        self.admin_edit_book_label_length.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_length = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                  placeholder_text="Enter Length", width=200,
                                                                  height=30,
                                                                  border_width=2, corner_radius=10)
        self.admin_edit_book_entry_length.grid(row=4, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_label_year = customtkinter.CTkLabel(self.admin_edit_book_frame, text="Year: ",
                                                                width=30, height=25,
                                                                corner_radius=7)
        self.admin_edit_book_label_year.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_year = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                placeholder_text="Enter Year", width=200,
                                                                height=30,
                                                                border_width=2, corner_radius=10)
        self.admin_edit_book_entry_year.grid(row=5, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_label_copies_available = customtkinter.CTkLabel(self.admin_edit_book_frame,
                                                                            text="Copies available: ",
                                                                            width=30, height=25,
                                                                            corner_radius=7)
        self.admin_edit_book_label_copies_available.grid(row=6, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_copies_available = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                            placeholder_text="Enter Copies available",
                                                                            width=200,
                                                                            height=30,
                                                                            border_width=2, corner_radius=10)
        self.admin_edit_book_entry_copies_available.grid(row=6, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_label_genre = customtkinter.CTkLabel(self.admin_edit_book_frame, text="Genre: ",
                                                                 width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_book_label_genre.grid(row=7, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_genre = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                 placeholder_text="Enter Genre", width=200,
                                                                 height=30,
                                                                 border_width=2, corner_radius=10)
        self.admin_edit_book_entry_genre.grid(row=7, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_label_description = customtkinter.CTkLabel(self.admin_edit_book_frame,
                                                                       text="Description: ",
                                                                       width=30, height=25,
                                                                       corner_radius=7)
        self.admin_edit_book_label_description.grid(row=8, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_book_entry_description = customtkinter.CTkEntry(self.admin_edit_book_frame,
                                                                       placeholder_text="Enter Description",
                                                                       width=200,
                                                                       height=30,
                                                                       border_width=2, corner_radius=10)
        self.admin_edit_book_entry_description.grid(row=8, column=1, padx=10, columnspan=2, pady=20)

        self.admin_edit_book_button_edit = customtkinter.CTkButton(self.admin_edit_book_frame,
                                                                 text="Edit", width=70, fg_color="#36719F",
                                                                 hover_color="#3B8ED0", text_color="#FFF",
                                                                 command=self.admin_button_edit_book)
        self.admin_edit_book_button_edit.grid(row=9, column=1, padx=60, pady=20, sticky='w')



        # admin delete book frame
        self.admin_delete_book_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_delete_book_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_delete_book_label_delete = customtkinter.CTkLabel(self.admin_delete_book_frame,
                                                               text="Delete book", width=60, height=20,
                                                               corner_radius=7)
        self.admin_delete_book_label_delete.grid(row=0, column=1, padx=80, pady=20, sticky='w')

        self.admin_delete_book_label_ID = customtkinter.CTkLabel(self.admin_delete_book_frame,
                                                                   text="Book ID: ", width=30, height=25,
                                                                   corner_radius=7)
        self.admin_delete_book_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_delete_book_entry_ID = customtkinter.CTkEntry(self.admin_delete_book_frame,
                                                                   placeholder_text="Enter Book ID",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.admin_delete_book_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_delete_book_button_delete = customtkinter.CTkButton(self.admin_delete_book_frame,
                                                                         text="Delete", width=70, fg_color="#36719F",
                                                                         hover_color="#3B8ED0", text_color="#FFF",
                                                                         command=self.admin_button_delete_book)
        self.admin_delete_book_button_delete.grid(row=2, column=1, padx=85, sticky='w')




        # admin add user page frame
        self.admin_add_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_add_user_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_add_user_label_add = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                                 text="Add user", width=60, height=20,
                                                                 corner_radius=7)
        self.admin_add_user_label_add.grid(row=0, column=1, padx=80, pady=20, sticky='w')

        self.admin_add_user_label_firstname = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                                      text="First Name: ", width=30, height=25,
                                                                      corner_radius=7)
        self.admin_add_user_label_firstname.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_firstname = customtkinter.CTkEntry(self.admin_add_user_frame,
                                                                      placeholder_text="Enter First Name",
                                                                      width=200, height=30, border_width=2,
                                                                      corner_radius=10)
        self.admin_add_user_entry_firstname.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_add_user_label_surname = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                                    text="Surname: ", width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_user_label_surname.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_surname = customtkinter.CTkEntry(self.admin_add_user_frame,
                                                                    placeholder_text="Enter Surname",
                                                                    width=200, height=30, border_width=2,
                                                                    corner_radius=10)
        self.admin_add_user_entry_surname.grid(row=2, column=1, padx=10, columnspan=2)

        self.admin_add_user_label_pid = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                                text="PID: ", width=30, height=25,
                                                                corner_radius=7)
        self.admin_add_user_label_pid.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_pid = customtkinter.CTkEntry(self.admin_add_user_frame,
                                                                placeholder_text="Enter PID",
                                                                width=200, height=30, border_width=2,
                                                                corner_radius=10)
        self.admin_add_user_entry_pid.grid(row=3, column=1, padx=10, columnspan=2)

        self.admin_add_user_label_address = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                                    text="Address: ", width=30, height=25,
                                                                    corner_radius=7)
        self.admin_add_user_label_address.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_address = customtkinter.CTkEntry(self.admin_add_user_frame,
                                                                    placeholder_text="Enter Address",
                                                                    width=200, height=30, border_width=2,
                                                                    corner_radius=10)
        self.admin_add_user_entry_address.grid(row=4, column=1, padx=10, columnspan=2)

        self.admin_add_user_label_username = customtkinter.CTkLabel(self.admin_add_user_frame,
                                                           text="Username: ", width=30, height=25, corner_radius=7)
        self.admin_add_user_label_username.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_username = customtkinter.CTkEntry(self.admin_add_user_frame, placeholder_text="Enter Username",
                                                           width=200, height=30, border_width=2, corner_radius=10)
        self.admin_add_user_entry_username.grid(row=5, column=1, padx=10, columnspan=2)

        self.admin_add_user_label_password = customtkinter.CTkLabel(self.admin_add_user_frame, text="Password: ", width=30, height=25,
                                                           corner_radius=7)
        self.admin_add_user_label_password.grid(row=6, column=0, padx=10, pady=20, sticky='e')

        self.admin_add_user_entry_password = customtkinter.CTkEntry(self.admin_add_user_frame,
                                                           placeholder_text="Enter Password", width=200, height=30,
                                                           border_width=2, corner_radius=10, show="•")
        self.admin_add_user_entry_password.grid(row=6, column=1, padx=10, columnspan=2, pady=20)

        self.admin_add_user_button_add = customtkinter.CTkButton(self.admin_add_user_frame,
                                                                   text="Add", width=70, fg_color="#36719F",
                                                                   hover_color="#3B8ED0", text_color="#FFF",
                                                                   command=self.admin_button_add_user)
        self.admin_add_user_button_add.grid(row=7, column=1, padx=60, sticky='w')





        # admin edit user page frame
        self.admin_edit_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_edit_user_frame.grid(row=1, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_edit_user_label_edit = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                     text="Edit user", width=60, height=20,
                                                                     corner_radius=7)
        self.admin_edit_user_label_edit.grid(row=0, column=1, padx=10, pady=20, sticky='e')

        self.admin_edit_user_label_id = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                      text="User ID: ", width=30, height=25,
                                                                      corner_radius=7)
        self.admin_edit_user_label_id.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_id = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                      placeholder_text="Enter User ID",
                                                                      width=200, height=30, border_width=2,
                                                                      corner_radius=10)
        self.admin_edit_user_entry_id.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_firstname = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                   text="First Name: ", width=30, height=25,
                                                                   corner_radius=7)
        self.admin_edit_user_label_firstname.grid(row=2, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_firstname = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                   placeholder_text="Enter First Name",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.admin_edit_user_entry_firstname.grid(row=2, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_surname = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                 text="Surname: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_user_label_surname.grid(row=3, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_surname = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                 placeholder_text="Enter Surname",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_edit_user_entry_surname.grid(row=3, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_pid = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                             text="PID: ", width=30, height=25,
                                                             corner_radius=7)
        self.admin_edit_user_label_pid.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_pid = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                             placeholder_text="Enter PID",
                                                             width=200, height=30, border_width=2,
                                                             corner_radius=10)
        self.admin_edit_user_entry_pid.grid(row=4, column=1, padx=10, columnspan=2)

        self.admin_edit_user_label_address = customtkinter.CTkLabel(self.admin_edit_user_frame,
                                                                 text="Address: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_edit_user_label_address.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_edit_user_entry_address = customtkinter.CTkEntry(self.admin_edit_user_frame,
                                                                 placeholder_text="Enter Address",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_edit_user_entry_address.grid(row=5, column=1, padx=10, columnspan=2)

        self.admin_edit_user_button_edit = customtkinter.CTkButton(self.admin_edit_user_frame,
                                                                    text="Edit", width=70, fg_color="#36719F",
                                                                    hover_color="#3B8ED0", text_color="#FFF",
                                                                    command=self.admin_button_edit_user)
        self.admin_edit_user_button_edit.grid(row=6, column=1, padx=10, pady=20, sticky='e')




        # admin delete user frame
        self.admin_delete_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_delete_user_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.admin_delete_user_label_delete = customtkinter.CTkLabel(self.admin_delete_user_frame,
                                                                     text="Delete user", width=60, height=20,
                                                                     text_color="red",
                                                                     corner_radius=7)
        self.admin_delete_user_label_delete.grid(row=0, column=1, padx=10, pady=20, sticky='e')

        self.admin_delete_user_label_ID = customtkinter.CTkLabel(self.admin_delete_user_frame,
                                                                   text="User ID: ", width=30, height=25,
                                                                   corner_radius=7)
        self.admin_delete_user_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_delete_user_entry_ID = customtkinter.CTkEntry(self.admin_delete_user_frame,
                                                                   placeholder_text="Enter User ID",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.admin_delete_user_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_delete_user_button_delete = customtkinter.CTkButton(self.admin_delete_user_frame,
                                                                         text="Delete", width=70, fg_color="#36719F",
                                                                         hover_color="#3B8ED0", text_color="#FFF",
                                                                         command=self.admin_button_delete_user)
        self.admin_delete_user_button_delete.grid(row=2, column=0, padx=0, sticky='e')



        # admin ban & unban user frame
        self.admin_ban_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_ban_user_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_ban_user_label_ban = customtkinter.CTkLabel(self.admin_ban_user_frame,
                                                              text="Ban User", width=60, height=20, text_color="red",
                                                              corner_radius=7)
        self.admin_ban_user_label_ban.grid(row=0, column=1, padx=10, pady=20, sticky='e')

        self.admin_ban_user_label_ID = customtkinter.CTkLabel(self.admin_ban_user_frame,
                                                                 text="User ID: ", width=30, height=25,
                                                                 corner_radius=7)
        self.admin_ban_user_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_ban_user_entry_ID = customtkinter.CTkEntry(self.admin_ban_user_frame,
                                                                 placeholder_text="Enter User ID",
                                                                 width=200, height=30, border_width=2,
                                                                 corner_radius=10)
        self.admin_ban_user_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_ban_user_button_ban = customtkinter.CTkButton(self.admin_ban_user_frame,
                                                                       text="Ban user", width=70, fg_color="#36719F",
                                                                       hover_color="#3B8ED0", text_color="#FFF",
                                                                       command=self.admin_button_ban_user)
        self.admin_ban_user_button_ban.grid(row=2, column=0, padx=0, sticky='e')

        self.admin_unban_user_label_unban = customtkinter.CTkLabel(self.admin_ban_user_frame,
                                                               text="Unban User", width=60, height=20, text_color="green",
                                                               corner_radius=7)
        self.admin_unban_user_label_unban.grid(row=4, column=1, padx=10, pady=20, sticky='e')

        self.admin_unban_user_label_ID = customtkinter.CTkLabel(self.admin_ban_user_frame,
                                                              text="User ID: ", width=30, height=25,
                                                              corner_radius=7)
        self.admin_unban_user_label_ID.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_unban_user_entry_ID = customtkinter.CTkEntry(self.admin_ban_user_frame,
                                                              placeholder_text="Enter User ID",
                                                              width=200, height=30, border_width=2,
                                                              corner_radius=10)
        self.admin_unban_user_entry_ID.grid(row=5, column=1, padx=10, columnspan=2)

        self.admin_unban_user_button_ban = customtkinter.CTkButton(self.admin_ban_user_frame,
                                                                 text="Unban user", width=70, fg_color="#36719F",
                                                                 hover_color="#3B8ED0", text_color="#FFF",
                                                                 command=self.admin_button_unban_user)
        self.admin_unban_user_button_ban.grid(row=6, column=0, padx=0, sticky='e')





        # admin verified & unverified user frame
        self.admin_verified_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_verified_user_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_verified_user_label_verified = customtkinter.CTkLabel(self.admin_verified_user_frame,
                                                               text="Verify User", width=60, height=20, text_color="green",
                                                               corner_radius=7)
        self.admin_verified_user_label_verified.grid(row=0, column=1, padx=10, pady=20, sticky='e')

        self.admin_verified_user_label_ID = customtkinter.CTkLabel(self.admin_verified_user_frame,
                                                              text="User ID: ", width=30, height=25,
                                                              corner_radius=7)
        self.admin_verified_user_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_verified_user_entry_ID = customtkinter.CTkEntry(self.admin_verified_user_frame,
                                                              placeholder_text="Enter User ID",
                                                              width=200, height=30, border_width=2,
                                                              corner_radius=10)
        self.admin_verified_user_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_verified_user_button_verified = customtkinter.CTkButton(self.admin_verified_user_frame,
                                                                 text="Verify user", width=70, fg_color="#36719F",
                                                                 hover_color="#3B8ED0", text_color="#FFF",
                                                                 command=self.admin_button_verified_user)
        self.admin_verified_user_button_verified.grid(row=2, column=0, padx=0, sticky='e')

        self.admin_unverified_user_label_unverified = customtkinter.CTkLabel(self.admin_verified_user_frame,
                                                                   text="Unverify User", width=60, height=20,
                                                                   text_color="red",
                                                                   corner_radius=7)
        self.admin_unverified_user_label_unverified.grid(row=4, column=1, padx=10, pady=20, sticky='e')

        self.admin_unverified_user_label_ID = customtkinter.CTkLabel(self.admin_verified_user_frame,
                                                                text="User ID: ", width=30, height=25,
                                                                corner_radius=7)
        self.admin_unverified_user_label_ID.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_unverified_user_entry_ID = customtkinter.CTkEntry(self.admin_verified_user_frame,
                                                                placeholder_text="Enter User ID",
                                                                width=200, height=30, border_width=2,
                                                                corner_radius=10)
        self.admin_unverified_user_entry_ID.grid(row=5, column=1, padx=10, columnspan=2)

        self.admin_unverified_user_button_unverified = customtkinter.CTkButton(self.admin_verified_user_frame,
                                                                   text="Unverify user", width=70, fg_color="#36719F",
                                                                   hover_color="#3B8ED0", text_color="#FFF",
                                                                   command=self.admin_button_unverified_user)
        self.admin_unverified_user_button_unverified.grid(row=6, column=0, padx=0, sticky='e')




        # admin accept & decline user changes frame
        self.admin_accept_user_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.admin_accept_user_frame.grid(row=2, column=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.admin_accept_user_label_accept = customtkinter.CTkLabel(self.admin_accept_user_frame,
                                                                         text="Accept user changes", width=60, height=20,
                                                                         text_color="green",
                                                                         corner_radius=7)
        self.admin_accept_user_label_accept.grid(row=0, column=1, padx=10, pady=20, sticky='e')

        self.admin_accept_user_label_ID = customtkinter.CTkLabel(self.admin_accept_user_frame,
                                                                   text="User ID: ", width=30, height=25,
                                                                   corner_radius=7)
        self.admin_accept_user_label_ID.grid(row=1, column=0, padx=10, pady=20, sticky='e')

        self.admin_accept_user_entry_ID = customtkinter.CTkEntry(self.admin_accept_user_frame,
                                                                   placeholder_text="Enter User ID",
                                                                   width=200, height=30, border_width=2,
                                                                   corner_radius=10)
        self.admin_accept_user_entry_ID.grid(row=1, column=1, padx=10, columnspan=2)

        self.admin_accept_user_button_accept = customtkinter.CTkButton(self.admin_accept_user_frame,
                                                                           text="Accept user changes", width=70,
                                                                           fg_color="#36719F",
                                                                           hover_color="#3B8ED0", text_color="#FFF",
                                                                           command=self.admin_button_accept_changes_user)
        self.admin_accept_user_button_accept.grid(row=2, column=0, padx=0, sticky='e')

        self.admin_decline_user_label_decline = customtkinter.CTkLabel(self.admin_accept_user_frame,
                                                                             text="Decline user changes", width=60, height=20,
                                                                             text_color="red",
                                                                             corner_radius=7)
        self.admin_decline_user_label_decline.grid(row=4, column=1, padx=10, pady=20, sticky='e')

        self.admin_decline_user_label_ID = customtkinter.CTkLabel(self.admin_accept_user_frame,
                                                                     text="User ID: ", width=30, height=25,
                                                                     corner_radius=7)
        self.admin_decline_user_label_ID.grid(row=5, column=0, padx=10, pady=20, sticky='e')

        self.admin_decline_user_entry_ID = customtkinter.CTkEntry(self.admin_accept_user_frame,
                                                                     placeholder_text="Enter User ID",
                                                                     width=200, height=30, border_width=2,
                                                                     corner_radius=10)
        self.admin_decline_user_entry_ID.grid(row=5, column=1, padx=10, columnspan=2)

        self.admin_decline_user_button_decline = customtkinter.CTkButton(self.admin_accept_user_frame,
                                                                               text="Decline user changes", width=70,
                                                                               fg_color="#36719F",
                                                                               hover_color="#3B8ED0", text_color="#FFF",
                                                                               command=self.admin_button_decline_changes_user)
        self.admin_decline_user_button_decline.grid(row=6, column=0, padx=0, sticky='e')




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
        self.navigation_frame_logged_main_button.configure(fg_color=("gray75", "gray25") if name == "main_page_logged" else "transparent")
        self.navigation_frame_logged_main_button.configure(fg_color=("gray75", "gray25") if name == "my_books" else "transparent")
        self.navigation_frame_logged_main_button.configure(fg_color=("gray75", "gray25") if name == "main" else "transparent")
        self.navigation_frame_logged_admin_main_button.configure(fg_color=("gray75", "gray25") if name == "main_admin" else "transparent")
        self.admin_add_author_button_add.configure(fg_color=("gray75", "gray25") if name == "add_author_admin" else "transparent")
        self.admin_edit_author_button_edit.configure(fg_color=("gray75", "gray25") if name == "edit_author_admin" else "transparent")
        self.admin_delete_author_button_delete.configure(fg_color=("gray75", "gray25") if name == "delete_author_admin" else "transparent")
        self.admin_add_book_button_add.configure(fg_color=("gray75", "gray25") if name == "add_book_admin" else "transparent")
        self.admin_edit_book_button_edit.configure(fg_color=("gray75", "gray25") if name == "edit_book_admin" else "transparent")
        self.admin_delete_book_button_delete.configure(fg_color=("gray75", "gray25") if name == "delete_book_admin" else "transparent")
        self.admin_add_user_button_add.configure(fg_color=("gray75", "gray25") if name == "add_user_admin" else "transparent")
        self.admin_edit_user_button_edit.configure(fg_color=("gray75", "gray25") if name == "edit_user_admin" else "transparent")
        self.admin_ban_user_button_ban.configure(fg_color=("gray75", "gray25") if name == "ban_user_admin" else "transparent")
        self.admin_verified_user_button_verified.configure(fg_color=("gray75", "gray25") if name == "verified_user_admin" else "transparent")
        self.admin_accept_user_button_accept.configure(fg_color=("gray75", "gray25") if name == "accept_changes_user_admin" else "transparent")
        self.admin_delete_user_button_delete.configure(fg_color=("gray75", "gray25") if name == "delete_user_admin" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            self.navigation_frame_logged.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
        else:
            self.home_frame.grid_forget()

        if name == "login":
            self.login_frame.grid(row=0, column=1, padx=(80, 20), pady=(20, 0), sticky="nsew")
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
        
        if name == "main_page_logged":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
            self.main_page_frame.grid_forget()
            self.main_page_logged_in_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.main_page_logged_in_user_frame.grid_forget()
        
        if name == "my_books":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged_admin.grid_forget()
            self.main_page_frame.grid_forget()
            self.my_book_loged_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.my_book_loged_user_frame.grid_forget()


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

        if name == "delete_author_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_delete_author_frame.grid(row=0, column=1, padx=(80, 0), pady=(20, 0), sticky="nsew")
        else:
            self.admin_delete_author_frame.grid_forget()

        if name == "add_book_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_add_book_frame.grid(row=0, column=1, padx=(53, 0), pady=(20, 0), sticky="nsew")
        else:
            self.admin_add_book_frame.grid_forget()

        if name == "edit_book_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_edit_book_frame.grid(row=0, column=1, padx=(53, 0), pady=(20, 0), sticky="nsew")
        else:
            self.admin_edit_book_frame.grid_forget()

        if name == "delete_book_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_delete_book_frame.grid(row=0, column=1, padx=(80, 20), pady=(20, 0), sticky="nsew")
        else:
            self.admin_delete_book_frame.grid_forget()

        if name == "add_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_add_user_frame.grid(row=0, column=1, padx=(80, 20), pady=(20, 0), sticky="nsew")
        else:
            self.admin_add_user_frame.grid_forget()

        if name == "edit_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_edit_user_frame.grid(row=0, column=1, padx=(80, 20), pady=(20, 0), sticky="nsew")
        else:
            self.admin_edit_user_frame.grid_forget()

        if name == "delete_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_delete_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_delete_user_frame.grid_forget()

        if name == "ban_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_ban_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_ban_user_frame.grid_forget()

        if name == "verified_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_verified_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_verified_user_frame.grid_forget()

        if name == "accept_changes_user_admin":
            self.navigation_frame.grid_forget()
            self.navigation_frame_logged.grid_forget()
            self.admin_accept_user_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_accept_user_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def login_button_event(self):
        self.select_frame_by_name("login")



    def login_button_log_user(self):
        mongo_client = get_mongo_client()
        username = self.login_entry_username.get()
        password = self.login_entry_password.get()
        #Admin: login_lib lib_12345
        #User: user password
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
                self.admin_add_author_entry_firstname.delete(0, "end")
                self.admin_add_author_entry_surname.delete(0, "end")
            else:
                print(added_author[1])
                self.select_frame_by_name("add_author_admin")


    def admin_button_edit_author_event(self):
        self.select_frame_by_name("edit_author_admin")

    def admin_button_edit_author(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_edit_author_entry_ID.get()
            firstname = self.admin_edit_author_entry_firstname.get()
            surname = self.admin_edit_author_entry_surname.get()
            edited_author = current_user.edit_author(mongo_client, id, firstname, surname)
            if edited_author[0] == True:
                self.select_frame_by_name("main_admin")
                print(edited_author[0])
                self.admin_edit_author_entry_ID.delete(0, "end")
                self.admin_edit_author_entry_firstname.delete(0, "end")
                self.admin_edit_author_entry_surname.delete(0, "end")
            else:
                print(edited_author[1])
                self.select_frame_by_name("edit_author_admin")


    def admin_button_delete_author_event(self):
        self.select_frame_by_name("delete_author_admin")

    def admin_button_delete_author(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_delete_author_entry_ID.get()
            deleted_author = current_user.delete_author(mongo_client, id)
            if deleted_author[0] == True:
                self.select_frame_by_name("main_admin")
                print(deleted_author[0])
                self.admin_delete_author_entry_ID.delete(0, "end")
            else:
                print(deleted_author[1])
                self.select_frame_by_name("delete_author_admin")


    def admin_button_add_book_event(self):
        self.select_frame_by_name("add_book_admin")


    def admin_button_add_book(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            title = self.admin_add_book_entry_title.get()
            author = self.admin_add_book_entry_author.get()
            length = self.admin_add_book_entry_length.get()
            year = self.admin_add_book_entry_year.get()
            copies_available = self.admin_add_book_entry_copies_available.get()
            genre = self.admin_add_book_entry_genre.get()
            description = self.admin_add_book_entry_description.get()
            count_borrowed = self.admin_add_book_entry_count_borrowed.get()
            if title != "" or author != "" or length != "" or year != "" or copies_available != "" or genre != "" or description != "" or count_borrowed != "":
                added_book = current_user.add_book(mongo_client, title, author, int(length), int(year), int(copies_available), genre, description, int(count_borrowed))
                if added_book[0] == True:
                    self.select_frame_by_name("main_admin")
                    print(added_book[0])
                    self.admin_add_book_entry_title.delete(0, "end")
                    self.admin_add_book_entry_author.delete(0, "end")
                    self.admin_add_book_entry_length.delete(0, "end")
                    self.admin_add_book_entry_year.delete(0, "end")
                    self.admin_add_book_entry_copies_available.delete(0, "end")
                    self.admin_add_book_entry_genre.delete(0, "end")
                    self.admin_add_book_entry_description.delete(0, "end")
                    self.admin_add_book_entry_count_borrowed.delete(0, "end")
                else:
                    print(added_book[1])
                    self.select_frame_by_name("add_book_admin")
            else:
                print("Fill the values properly")



    def admin_button_edit_book_event(self):
        self.select_frame_by_name("edit_book_admin")

    def admin_button_edit_book(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            book_id = self.admin_edit_book_entry_book_ID.get()
            title = self.admin_edit_book_entry_title.get()
            author = self.admin_edit_book_entry_author.get()
            length = self.admin_edit_book_entry_length.get()
            year = self.admin_edit_book_entry_year.get()
            copies_available = self.admin_edit_book_entry_copies_available.get()
            genre = self.admin_edit_book_entry_genre.get()
            description = self.admin_edit_book_entry_description.get()
            if book_id != "" or title != "" or author != "" or length != "" or year != "" or copies_available != "" or genre != "" or description != "":
                edited_book = current_user.edit_book(mongo_client, book_id, title, author, int(length), int(year), int(copies_available), genre, description)
                if edited_book[0] == True:
                    self.select_frame_by_name("main_admin")
                    print(edited_book[0])
                    self.admin_edit_book_entry_book_ID.delete(0, "end")
                    self.admin_edit_book_entry_title.delete(0, "end")
                    self.admin_edit_book_entry_author.delete(0, "end")
                    self.admin_edit_book_entry_length.delete(0, "end")
                    self.admin_edit_book_entry_year.delete(0, "end")
                    self.admin_edit_book_entry_copies_available.delete(0, "end")
                    self.admin_edit_book_entry_genre.delete(0, "end")
                    self.admin_edit_book_entry_description.delete(0, "end")
                else:
                    print(edited_book[1])
                    self.select_frame_by_name("edit_book_admin")
            else:
                print("Fill the values properly")


    def admin_button_delete_book_event(self):
        self.select_frame_by_name("delete_book_admin")

    def admin_button_delete_book(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_delete_book_entry_ID.get()
            deleted_book = current_user.delete_book(mongo_client, id)
            if deleted_book[0] == True:
                self.select_frame_by_name("main_admin")
                print(deleted_book[0])
                self.admin_delete_book_entry_ID.delete(0, "end")
            else:
                print(deleted_book[1])
                self.select_frame_by_name("delete_book_admin")


    def admin_button_add_user_event(self):
        self.select_frame_by_name("add_user_admin")

    def admin_button_add_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            firstname = self.admin_add_user_entry_firstname.get()
            surname = self.admin_add_user_entry_surname.get()
            pid = self.admin_add_user_entry_pid.get()
            address = self.admin_add_user_entry_address.get()
            login = self.admin_add_user_entry_username.get()
            password = self.admin_add_user_entry_password.get()
            if firstname != "" or surname != "" or pid != "" or address != "" or login != "" or password != "":
                added_user = current_user.admin_create_account(mongo_client, firstname, surname, int(pid), address, login, password)
                if added_user[0] == True:
                    self.select_frame_by_name("main_admin")
                    print(added_user[0])
                    self.admin_add_user_entry_firstname.delete(0, "end")
                    self.admin_add_user_entry_surname.delete(0, "end")
                    self.admin_add_user_entry_pid.delete(0, "end")
                    self.admin_add_user_entry_address.delete(0, "end")
                    self.admin_add_user_entry_username.delete(0, "end")
                    self.admin_add_user_entry_password.delete(0, "end")
                else:
                    print(added_user[1])
                    self.select_frame_by_name("add_user_admin")
            else:
                print("Fill the values properly")

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
            if firstname != "" or surname != "" or pid != "" or address != "" or id != "":
                edited_user = current_user.edit_user(mongo_client, firstname, surname, int(pid), address, _id = id)
                if edited_user[0] == True:
                    self.select_frame_by_name("main_admin")
                    print(edited_user[0])
                    self.admin_edit_user_entry_id.delete(0, "end")
                    self.admin_edit_user_entry_firstname.delete(0, "end")
                    self.admin_edit_user_entry_surname.delete(0, "end")
                    self.admin_edit_user_entry_pid.delete(0, "end")
                    self.admin_edit_user_entry_address.delete(0, "end")
                else:
                    print(edited_user[1])
                    self.select_frame_by_name("edit_user_admin")
            else:
                print("Fill the values properly")

    def admin_button_delete_user_event(self):
        self.select_frame_by_name("delete_user_admin")

    def admin_button_delete_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_delete_user_entry_ID.get()
            deleted_user = current_user.delete_user(mongo_client, id)
            if deleted_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(deleted_user[0])
                self.admin_delete_book_entry_ID.delete(0, "end")
            else:
                print(deleted_user[1])
                self.select_frame_by_name("delete_user_admin")

    def admin_button_ban_user_event(self):
        self.select_frame_by_name("ban_user_admin")

    def admin_button_ban_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_ban_user_entry_ID.get()
            banned_user = current_user.ban_user(mongo_client, id)
            if banned_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(banned_user[0])
                self.admin_ban_user_entry_ID.delete(0, "end")
            else:
                print(banned_user[1])
                self.select_frame_by_name("ban_user_admin")

    def admin_button_unban_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_unban_user_entry_ID.get()
            unbanned_user = current_user.unban_user(mongo_client, id)
            if unbanned_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(unbanned_user[0])
                self.admin_unban_user_entry_ID.delete(0, "end")
            else:
                print(unbanned_user[1])
                self.select_frame_by_name("ban_user_admin")

    def admin_button_verified_user_event(self):
        self.select_frame_by_name("verified_user_admin")

    def admin_button_verified_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_verified_user_entry_ID.get()
            verified_user = current_user.verified_user(mongo_client, id)
            if verified_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(verified_user[0])
                self.admin_verified_user_entry_ID.delete(0, "end")
            else:
                print(verified_user[1])
                self.select_frame_by_name("verified_user_admin")

    def admin_button_unverified_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_unverified_user_entry_ID.get()
            unverified_user = current_user.unverified_user(mongo_client, id)
            if unverified_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(unverified_user[0])
                self.admin_unverified_user_entry_ID.delete(0, "end")
            else:
                print(unverified_user[1])
                self.select_frame_by_name("verified_user_admin")

    def admin_button_accept_changes_user_event(self):
        self.select_frame_by_name("accept_changes_user_admin")

    def admin_button_accept_changes_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_accept_user_entry_ID.get()
            accepted_user = current_user.accept_user_changes(mongo_client, id)
            if accepted_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(accepted_user[0])
                self.admin_verified_user_entry_ID.delete(0, "end")
            else:
                print(accepted_user[1])
                self.select_frame_by_name("accept_changes_user_admin")

    def admin_button_decline_changes_user(self):
        if current.role == Roles.Librarian.name:
            current_user = Librarian(current)
            id = self.admin_decline_user_entry_ID.get()
            declined_user = current_user.decline_user_changes(mongo_client, id)
            if declined_user[0] == True:
                self.select_frame_by_name("main_admin")
                print(declined_user[0])
                self.admin_decline_user_entry_ID.delete(0, "end")
            else:
                print(declined_user[1])
                self.select_frame_by_name("accept_changes_user_admin")

    def navigation_frame_admin_main_page_event(self):
        self.select_frame_by_name("main_admin")

    def show_next_book_my_page(self):
        global CURRENT_USER_BORROWED_BOOKS
        global CURRENT_USER_SELECTED_MY_BOOK
        if len(CURRENT_USER_BORROWED_BOOKS) == 0:
            return
        current_user = User(current)
        CURRENT_USER_BORROWED_BOOKS = get_all_borrowed_books_from_user(mongo_client, current._id)
        
        CURRENT_USER_SELECTED_MY_BOOK +=1
        if CURRENT_USER_SELECTED_MY_BOOK >= len(CURRENT_USER_BORROWED_BOOKS):
            CURRENT_USER_SELECTED_MY_BOOK = 0
        
        
        self.textbox_author_my_books_page.configure(state="normal")
        self.textbox_book_description_my_books_page.configure(state="normal")
        self.textbox_title_my_books_page.configure(state="normal")
        
        self.textbox_author_my_books_page.delete(0.0,"end")
        self.textbox_book_description_my_books_page.delete(0.0,"end")
        self.textbox_title_my_books_page.delete(0.0,"end")
        
        book=current_user.user_find_book(mongo_client,CURRENT_USER_BORROWED_BOOKS[CURRENT_USER_SELECTED_MY_BOOK])
        author = find_author(mongo_client,book['author'])
        name =book["_id"]
        path_to_book_image = os.path.join(PATH_TO_LOCAL_IMAGES_BOOKS, f"{name}.jpg")
        if os.path.isfile(path_to_book_image):
            path_to_image = path_to_book_image
        else:
            path_to_image = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Icons", "placeholder_no_book.png")
        self.book_image_my_books_page.configure(image=customtkinter.CTkImage(Image.open(path_to_image), size=(200, 300)))    
        self.textbox_author_my_books_page.insert("0.0",f"{author[1]['first_name']} {author[1]['surname']}")
        self.textbox_book_description_my_books_page.insert("0.0",f"{book['description']}")
        self.textbox_title_my_books_page.insert("0.0",f"{book['title']}")
    
    def show_next_book_main_page(self):
        global CURRENT_SELECTED_BOOK_MAIN_PAGE
        global ALL_LIBRARY_BOOKS
        CURRENT_SELECTED_BOOK_MAIN_PAGE +=1
        if CURRENT_SELECTED_BOOK_MAIN_PAGE >= len(ALL_LIBRARY_BOOKS):
            CURRENT_SELECTED_BOOK_MAIN_PAGE = 0
        
        self.textbox_title_main_page.configure(state="normal")
        self.textbox_author_main_page.configure(state="normal")
        self.textbox_book_description_main_page.configure(state="normal")
        
        self.textbox_title_main_page.delete(0.0,"end")
        self.textbox_author_main_page.delete(0.0,"end")
        self.textbox_book_description_main_page.delete(0.0,"end")
        
        path_to_image = self.get_path_to_local_image(ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE])
        if path_to_image == None:
            path_to_image = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Icons", "placeholder_no_book.png",)
        self.book_image_main_page.configure(image=customtkinter.CTkImage(Image.open(path_to_image), size=(200, 300)))
        self.textbox_title_main_page.insert("0.0",f"{ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['title']}")
        self.textbox_title_main_page.configure(state="disabled")
        author = find_author(mongo_client=mongo_client,_id =ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['author'])
        self.textbox_author_main_page.insert("0.0",f"{author[1]['first_name']} {author[1]['surname']}")
        self.textbox_author_main_page.configure(state="disabled")
        self.textbox_book_description_main_page.insert("0.0",f"{ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['description']}")
        self.textbox_book_description_main_page.configure(state="disabled")
        
    
    def return_book_user(self):
        current_user = User(current)
        print(current_user.return_book(mongo_client, CURRENT_USER_BORROWED_BOOKS[CURRENT_USER_SELECTED_MY_BOOK])[1])
        del CURRENT_USER_BORROWED_BOOKS[CURRENT_USER_SELECTED_MY_BOOK]
        self.show_my_book(1)
        
        


    def borrow_book_user(self):
        current_user =User(current)
        print(current_user.borrow_book(mongo_client,ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['_id'])[1])
    
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
        registration_result = create_account(mongo_client, firstname, surname, int(pid), address, username, password)
        register_user = registration_result[0]
        if register_user == True:
            self.select_frame_by_name("login")
            print(registration_result[0])
            self.registration_entry_firstname.delete(0, "end")
            self.registration_entry_surname.delete(0, "end")
            self.registration_entry_pid.delete(0, "end")
            self.registration_entry_address.delete(0, "end")
            self.registration_entry_username.delete(0, "end")
            self.registration_entry_password.delete(0, "end")
        else:
            print(registration_result[1])


    def main_button_event(self):
        self.select_frame_by_name("register")




    def get_all_books_localy(self,all_books_from_db):
        for book in all_books_from_db:
            name =book["_id"]
            path_to_book_image = os.path.join(PATH_TO_LOCAL_IMAGES_BOOKS, f"{name}.jpg")
            if not os.path.isfile(path_to_book_image):
                image_data = book["image"]
                if image_data is not None:
                    with open(path_to_book_image, "wb") as binary_file:
                        binary_file.write(image_data)
    
    def get_path_to_local_image(self,book):
        name =book["_id"]
        path_to_book_image = os.path.join(PATH_TO_LOCAL_IMAGES_BOOKS, f"{name}.jpg")
        if os.path.isfile(path_to_book_image):
            return path_to_book_image
        return None
            
    def navigation_frame_logged_main_page_event(self):
        global CURRENT_SELECTED_BOOK_MAIN_PAGE
        global ALL_LIBRARY_BOOKS
        ALL_LIBRARY_BOOKS = find_all_books(mongo_client)
        if CURRENT_SELECTED_BOOK_MAIN_PAGE >= len(ALL_LIBRARY_BOOKS):
            CURRENT_SELECTED_BOOK_MAIN_PAGE = 0
        self.textbox_title_main_page.configure(state="normal")
        self.textbox_author_main_page.configure(state="normal")
        self.textbox_book_description_main_page.configure(state="normal")
        
        self.textbox_title_main_page.delete(0.0,"end")
        self.textbox_author_main_page.delete(0.0,"end")
        self.textbox_book_description_main_page.delete(0.0,"end")
        
        self.get_all_books_localy(ALL_LIBRARY_BOOKS)
        path_to_image = self.get_path_to_local_image(ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE])
        if path_to_image == None:
            path_to_image = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Icons", "placeholder_no_book.png")
        self.book_image_main_page.configure(image=customtkinter.CTkImage(Image.open(path_to_image), size=(200, 300)))
        self.textbox_title_main_page.insert("0.0",f"{ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['title']}")
        author = find_author(mongo_client=mongo_client,_id =ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['author'])
        self.textbox_author_main_page.insert("0.0",f"{author[1]['first_name']} {author[1]['surname']}")
        self.textbox_book_description_main_page.insert("0.0",f"{ALL_LIBRARY_BOOKS[CURRENT_SELECTED_BOOK_MAIN_PAGE]['description']}")
        self.textbox_title_main_page.configure(state="disabled")
        self.textbox_author_main_page.configure(state="disabled")
        self.textbox_book_description_main_page.configure(state="disabled")
        self.select_frame_by_name("main_page_logged")
        
    def show_my_book(self,move_index):
        global CURRENT_USER_BORROWED_BOOKS
        global CURRENT_USER_SELECTED_MY_BOOK
        current_user = User(current)
        CURRENT_USER_BORROWED_BOOKS = get_all_borrowed_books_from_user(mongo_client, current._id)
        CURRENT_USER_SELECTED_MY_BOOK +=move_index
        if CURRENT_USER_SELECTED_MY_BOOK >= len(CURRENT_USER_BORROWED_BOOKS):
            CURRENT_USER_SELECTED_MY_BOOK = 0
        
        self.textbox_author_my_books_page.configure(state="normal")
        self.textbox_book_description_my_books_page.configure(state="normal")
        self.textbox_title_my_books_page.configure(state="normal")
        
        self.textbox_author_my_books_page.delete(0.0,"end")
        self.textbox_book_description_my_books_page.delete(0.0,"end")
        self.textbox_title_my_books_page.delete(0.0,"end")
        
        if len(CURRENT_USER_BORROWED_BOOKS) == 0:
            self.book_image_my_books_page.configure(image=self.no_book_image)
            self.textbox_author_my_books_page.insert("0.0","You have yet to borrow a book")
            self.textbox_book_description_my_books_page.insert("0.0","You have yet to borrow a book")
            self.textbox_title_my_books_page.insert("0.0","You have yet to borrow a book")
        else:
            book=current_user.user_find_book(mongo_client,CURRENT_USER_BORROWED_BOOKS[CURRENT_USER_SELECTED_MY_BOOK])
            author = find_author(mongo_client,book['author'])
            name =book["_id"]
            path_to_book_image = os.path.join(PATH_TO_LOCAL_IMAGES_BOOKS, f"{name}.jpg")
            if os.path.isfile(path_to_book_image):
                path_to_image = path_to_book_image
            else:
                path_to_image = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Icons", "placeholder_no_book.png")
            self.book_image_my_books_page.configure(image=customtkinter.CTkImage(Image.open(path_to_image), size=(200, 300)))    
            self.textbox_author_my_books_page.insert("0.0",f"{author[1]['first_name']} {author[1]['surname']}")
            self.textbox_book_description_my_books_page.insert("0.0",f"{book['description']}")
            self.textbox_title_my_books_page.insert("0.0",f"{book['title']}")
    
    def navigation_frame_logged_admin_logout_button_event(self):
        self.select_frame_by_name("login")
        self.login_entry_password.delete(0, "end")
    
    def navigation_frame_logged_my_books_button_event(self):
        
        self.show_my_book(0)
        self.select_frame_by_name("my_books")
        

    
def check_local_storage_exists():
    if not os.path.exists(PATH_TO_LOCAL_IMAGES_BOOKS):
        os.makedirs(PATH_TO_LOCAL_IMAGES_BOOKS)
    return
    

if __name__ == "__main__":
    check_local_storage_exists()
    app = App()
    app.mainloop()