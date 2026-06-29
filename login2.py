from tkinter import *
import tkinter as tk
import platform
import uuid
import geocoder
import hashlib
from datetime import datetime
from database import UserDBManager, ActivityTable 

class LoginSignupFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_page = "login"  # Track current page
        
        
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
        
        # Function to handle login button click
    def login_clicked(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.user = User(self.username, self.password)
        self.validate = self.validate_login()
        activity_table = ActivityTable()
        print(str(self.username),str(self.password),self.validate,str(self.user.get_mac_address()),str(self.user.get_device_name()),str(self.login_description))
        print()
        print()
        print()
        print()
        print()
        
        activity_table.add_activity(str(self.username),str(self.password),self.validate,str(self.user.get_mac_address()),str(self.user.get_device_name()),str(self.login_description))
        

        
    def validate_login(self):
        self.DBManager = UserDBManager()
        self.df = self.DBManager.get_all_users()
        
        self.check_username = self.username in self.df['username'].values
        self.check_password = self.password in self.df['password'].values
        self.check_device_name = self.user.get_device_name() in self.df['deviceName'].values
        self.check_mac_address = self.user.get_mac_address() in self.df['macAddress'].values
        
        if not(self.check_username):
            self.login_description = "uesrname error"
            return False
        
        elif not(self.check_password):
            self.login_description = "password error"
            return False
        
        elif not(self.check_device_name):
            self.login_description = "device name error"
        
        elif not(self.check_mac_address):
            self.check_mac_address = "mac address error"
        
        else:
            Label(self.login_frame, text="Login Successful").grid(row=3, column=0, columnspan=2)
        return True




class User:
    
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.sessionStart = datetime.now()
        self.validity = True
        self.location = {}
        
        
    def get_mac_address(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        return mac

    def get_device_name(self):
        # Get the name of the current device
        current_device = platform.node()
        self.logged_in_mac = hex(uuid.getnode())
        return self.logged_in_mac
    
    def get_start_time(self):
        return self.sessionStart.strftime("%H:%M:%S")
    
    def get_place(self):
        lng = geocoder.ip('me').lng
        lat = geocoder.ip('me').lat
        self.location["lng"]=lng
        self.location["lat"]=lat
        return self.location

if __name__ == "__main__":
    # Create the main tkinter window
    root = tk.Tk()
    root.title("Login and Signup Example")

    # Create an instance of LoginSignupFrame and pack it into the tkinter window
    login_signup_frame = LoginSignupFrame(root)
    login_signup_frame.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

    # Make the root window resizable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)


    # Run the tkinter main loop
    root.mainloop()


    # Example usage
    user1 = User("john_doe", "password123")

    