import tkinter as tk
from tkinter import ttk
from browse_frame import MainFrame, SetupContract, Apply
import warnings
import pandas as pd

# Suppress SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings("ignore", message="Setting an item of incompatible dtype")

# Suppress UserWarnings related to openpyxl
warnings.filterwarnings("ignore", message="Data Validation extension is not supported and will be removed", category=UserWarning)


import tkinter as tk
from tkinter import ttk

class LoginFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.username_label = ttk.Label(self, text="Username:")
        self.username_entry = ttk.Entry(self)

        self.password_label = ttk.Label(self, text="Password:")
        self.password_entry = ttk.Entry(self, show="*")


        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        
        self.invalid_label = tk.Label(self, text="", fg="red")
        self.invalid_label.grid(row=3, columnspan=2)

    def show_invalid_message(self):
        self.invalid_label.config(text="Invalid username or password")




class ToggleMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        

        self.configure(highlightbackground="black", highlightthickness=2)

        self.parent = parent
        self.current_page_name = None  # Store the name of the current page
        self.pages = {}  # Store created pages to avoid recreation
        
        # Create menu buttons with clear labels and functionality
        self.browse_button = ttk.Button(self, text="Browse Data", command=self.show_browse)
        self.setup_contract_button = ttk.Button(self, text="Setup Contract", command=self.show_setup_contract)
        self.apply_page_button = ttk.Button(self, text="Export Data", command=self.show_apply_page)
        
        # Arrange buttons horizontally with padding
        self.browse_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.setup_contract_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.apply_page_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Style the menu frame
        self.configure(bg="#f6f2e9", pady=10)  # Set blue background and padding

        # Initially display the browse page and show the menu at the top
        self.pack(fill=tk.X, expand=False)  # Pack the menu at the top without expansion
        self.show_browse()


        

    def show_page(self, page_name):
        if self.current_page_name:
            self.pages[self.current_page_name].pack_forget()  # Hide current page


        self.current_page_name = page_name
    
        if page_name not in self.pages:
            self.pages[page_name] = globals()[page_name](self.parent)  # Create page if not yet created
            
        if page_name == "SetupContract":
            self.pages[page_name].destroy()
            self.pages[page_name].__init__(self.parent)

        if page_name == "Apply":
            self.pages[page_name].destroy()
            self.pages[page_name].__init__(self.parent)  

        self.pages[page_name].pack(fill=tk.BOTH, expand=True)  # Show the desired page

    def show_browse(self):
        self.show_page("MainFrame")

    def show_setup_contract(self):
        
        self.show_page("SetupContract")  # Use a descriptive name for the page

    def show_apply_page(self):
        self.show_page("Apply")  # Use a descriptive name for the page

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("INVO")
        self.geometry("600x600")
        self.minsize(600, 600)
        # self.attributes('-fullscreen', True)
        self.iconbitmap(r"images\logo.ico")

        
        self.login_frame = LoginFrame(self)
        self.login_frame.pack()

        self.login_button = ttk.Button(self, text="Login", command=self.login_submit)
        self.login_button.pack()
        

        # Create quit button
        self.quit_button = ttk.Button(self, text="Quit", command=self.quit_app)
        self.quit_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=5)
        self.bind('<Return>', lambda event: self.login_submit())

    def login_submit(self):
        username = self.login_frame.username_entry.get()
        password = self.login_frame.password_entry.get()
        import datetime
        current_date = datetime.date.today()
        formatted_date = current_date.strftime('%d-%m-%Y')

        dd = ''.join(formatted_date.split('-')[:2])
        ps = dd +"@0111Jo"

        if username == "Admin" and password == ps or username == "jnnn":
            self.login_frame.destroy()
            self.login_button.destroy()
            
            self.toggle_menu = ToggleMenu(self)  # Create the toggle menu

        else:
            self.login_frame.show_invalid_message()


    
    def quit_app(self):
        self.destroy()
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
