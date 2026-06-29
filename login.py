from tkinter import *
import tkinter as tk
import platform
import uuid
import geocoder
import hashlib
from datetime import datetime
from database import UserDBManager, ActivityTable 

class Login_page(Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.current_page = "login"
        self.create_login_page()

        self.login_frame.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Make the columns and rows expandable
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
    def create_login_page(self):
        self.login_frame = Frame(self)

        # Login labels and entries
        self.username_label = Label(self.login_frame, text="Username:")
        self.username_entry = Entry(self.login_frame)
        self.password_label = Label(self.login_frame, text="Password:")
        self.password_entry = Entry(self.login_frame, show="*")

        # Login and Signup buttons
        self.login_button = Button(self.login_frame, text="Login", command=self.login_clicked)

        # Packing the login page elements using grid
        self.username_label.grid(row=0, column=0, sticky="w")
        self.username_entry.grid(row=0, column=1)
        self.password_label.grid(row=1, column=0, sticky="w")
        self.password_entry.grid(row=1, column=1)
        self.login_button.grid(row=2, column=0, columnspan=2)
        
        # Function to handle login button clic
        
    def login_clicked(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        print(self.username)
        print(self.password)
    
if __name__ == "__main__":
    # Create the main tkinter window
    root = tk.Tk()
    root.title("Login and Signup Example")

    # Create an instance of LoginSignupFrame and pack it into the tkinter window
    login_signup_frame = Login_page(root)
    login_signup_frame.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

    # Make the root window resizable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)


    # Run the tkinter main loop
    root.mainloop()

