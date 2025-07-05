# Import necessary libraries
from tkinter import *  # Core Tkinter module
import tkinter as tk
from tkinter import ttk  # Themed Tkinter widgets
from tkinter import filedialog  # File dialog module
from tkinter.filedialog import askopenfilenames  # For selecting multiple files
import pandas as pd  # Data manipulation library
from tkinter import Scrollbar  # For adding scrollbars
from file_uploader import FileUploader  # Custom module for handling file uploads
from tkcalendar import Calendar, DateEntry  # Calendar widgets
from PIL import Image, ImageTk  # For handling and displaying images
from contract import Contract  # Custom module for contract-related functionality
import sqlite3  # SQLite database library
from invoice import Invoice  # Custom module for invoice-related functionality
import os  # For file and directory operations
import sys  # System-specific parameters and functions
from pandastable import Table  # Library for displaying pandas DataFrames in Tkinter
import numpy as np  # Numerical operations library
import warnings  # For suppressing warnings

from format_excel import FormatExcel
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import pandas as pd
from pathlib import Path
from tabulate import tabulate


# Global configurations and warnings suppression
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy of a slice from a DataFrame.*")
warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option('mode.chained_assignment', None)  # Disable chained assignment warnings
pd.set_option('display.max_columns', None)  # Display all DataFrame columns
pd.set_option('display.width', None)  # Auto-adjust DataFrame display width
pd.set_option('display.colheader_justify', 'center')  # Center column headers in DataFrame display

# Function to resolve resource paths for development and PyInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Global variable for setup name (if applicable)
global_setup_name = ""

# MainFrame class: Manages the main application frame
class MainFrame(ttk.Frame):
    def __init__(self, parent):
        """Initialize the main application frame."""
        super().__init__(parent)
        
        # Load and resize the background image
        image = Image.open(resource_path(r"images\bg.png"))
        desired_width, desired_height = 600, 600
        image.thumbnail((desired_width, desired_height))
        photo = ImageTk.PhotoImage(image)

        # Display the image in a label
        self.image_label = tk.Label(self, image=photo)
        self.image_label.image = photo  # Keep reference to prevent garbage collection
        self.image_label.pack()

        # Create a canvas for dynamic content and scrolling
        global container
        container = []  # Container to hold FileUploader instances
        self.canvas = tk.Canvas(self, background="#f0f0f0", scrollregion=(0, 0, self.winfo_width(), 800))
        self.canvas.pack(expand=True, fill='both')

        # Add a Welcome frame as the initial content
        self.welcome = Welcome(self)
        ttk.Label(self.welcome).pack()
        self.canvas.create_window((-1, 0), window=self.welcome, anchor='nw', width=self.winfo_width(), height=270)

        # Bind events for resizing and scrolling
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(-int(event.delta / 60), 'units'))
        self.bind('<Configure>', self.update_size)

    def update_size(self, event):
        """Update the size of the Welcome frame dynamically."""
        self.canvas.create_window((-1, 0), window=self.welcome, anchor='nw', width=self.winfo_width(), height=270)

# ExcelFileBrowserApp class: Handles file selection and management
class ExcelFileBrowserApp:
    def __init__(self, root):
        """Initialize the file browser application."""
        self.root = root
        self.files = []  # List to store selected file paths

        # Create a frame for the file list
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add a listbox with a scrollbar for displaying files
        self.scrollbar = Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self.list_frame, selectmode=tk.MULTIPLE, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for action buttons
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X)

        # Add buttons for browsing and removing files
        self.browse_button = tk.Button(self.buttons_frame, text="Select files", command=self.browse_files)
        self.browse_button.pack(side=tk.LEFT)
        self.remove_button = tk.Button(self.buttons_frame, text="Remove Selected", command=self.remove_selected_files)
        self.remove_button.pack(side=tk.LEFT)

    def browse_files(self):
        """Open a file dialog to select Excel files."""
        file_paths = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xlsx *.xls")])
        for file_path in file_paths:
            self.files.append(file_path)
            self.listbox.insert(tk.END, os.path.basename(file_path))  # Display only the file name

        # Initialize FileUploader instances for the selected files
        global container
        try:
            container = [FileUploader(file_path) for file_path in self.files]
            #print(len(container), "files successfully loaded.")
        except Exception as e:
            messagebox.showerror("Error", "Failed to initialize FileUploader instances for selected files, probably due to statment sheet missing")
            print(e)
            container = [FileUploader(file_path) for file_path in self.files]

    def remove_selected_files(self):
        """Remove selected files from the list."""
        selected_indices = self.listbox.curselection()
        for i in reversed(selected_indices):  # Reverse to avoid index shifting
            self.listbox.delete(i)
            del self.files[i]
            del container[i]

# Welcome class: Displays a welcome interface
class Welcome(ttk.Frame):
    def __init__(self, parent):
        """Initialize the Welcome frame."""
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        ExcelFileBrowserApp(self)  # Embed the file browser app within the welcome frame

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################






import tkinter as tk
from tkinter import ttk
import sqlite3

class SetupContract(ttk.Frame):
    """Scrollable container frame for contract configuration settings."""
    
    def __init__(self, parent):
        """
        Initialize the scrollable contract setup interface.
        
        Args:
            parent: Parent widget container
        """
        super().__init__(parent)
        self.pack(expand=True, fill="both")

        # --------------------------
        # Scrollable Canvas Setup
        # --------------------------
        self.canvas = tk.Canvas(self, background="red", 
                              scrollregion=(0, 0, self.winfo_width(), 20000))
        self.canvas.pack(expand=True, fill='both')
        
        # --------------------------
        # Scrollbar Configuration
        # --------------------------
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", 
                                     command=self.canvas.yview)
        self.scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # --------------------------
        # Content Initialization
        # --------------------------
        self.contract_setting = ContractSetting(self)
        
        # --------------------------
        # Event Bindings
        # --------------------------
        self.canvas.bind_all('<MouseWheel>', lambda event: 
                           self.canvas.yview_scroll(-int(event.delta / 60), 'units'))
        self.bind('<Configure>', self.update_size)

    def update_size(self, event):
        """Handle window resize events to maintain proper canvas dimensions."""
        self.canvas.create_window((-1, 0), window=self.contract_setting, 
                                anchor='nw', width=self.winfo_width(), height=20000)

class DotDict:
    """Dictionary wrapper allowing attribute-style access to keys."""
    
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)
        
    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return self.__dict__[key]
        
    def __getattr__(self, key):
        """Fallback for missing attributes."""
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{key}'")

class ContractSetting(ttk.Frame):
    """Main interface for managing contract configurations and setups."""
    
    def __init__(self, parent):
        """
        Initialize contract configuration management interface.
        
        Args:
            parent: Parent widget container
        """
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.name_contract_dict = {contract.filename: contract for contract in container}
        self.current_file = None

        # --------------------------
        # UI Component Initialization
        # --------------------------
        self.create_file_selection()
        self.create_setup_controls()
        self.create_contract_frame()

    def create_file_selection(self):
        """Create file selection listbox and related UI elements."""
        tk.Label(self, text="choose file", font=("Helvetica", 10, "underline")
               ).grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        self.setup_file = tk.Listbox(self, 
                                   listvariable=tk.StringVar(value=[file.filename for file in container]))
        self.setup_file.bind('<Double-1>', self.refresh_page)
        self.initialized_setup = None
        self.setup_file.grid(row=1, column=0, sticky="w", padx=5, pady=10, rowspan=8)

    def create_setup_controls(self):
        """Create setup selection and management controls."""
        # Setup selection combobox
        tk.Label(self, text="change setup", font=("Helvetica", 10, "underline")
               ).grid(column=0, sticky="w", padx=0, pady=0)
        
        table_names = ['None'] + list(get_tables().keys())
        self.initialized_setup = ttk.Combobox(self, values=table_names)
        self.initialized_setup.grid(column=0, sticky="w", padx=5, pady=10)
        self.initialized_setup.bind("<<ComboboxSelected>>", self.refresh_page)

        # Setup management buttons
        self.delete_button = tk.Button(self, text="Delete setup", 
                                     command=self.deactivate_table_column)
        self.delete_button.grid(row=0, column=0, padx=5, pady=15)

    def create_contract_frame(self):
        """Initialize the main contract configuration frame."""
        self.contract_frame = ContractFrame(self)
        self.contract_frame.grid(column=0, columnspan=2)

    def refresh_page(self, event):
        """Refresh the contract configuration interface with new selections."""
        # Destroy existing frame
        if hasattr(self, 'contract_frame'):
            self.contract_frame.destroy()

        # Get selected file and setup
        selected_index = self.setup_file.curselection()
            
        if not selected_index:
            self.current_file = ""
        else:
            self.current_file = self.name_contract_dict[self.setup_file.get(selected_index[0])]

        current_setup = self.get_current_setup_config()

        # Reinitialize contract frame
        self.contract_frame = ContractFrame(self, self.current_file, current_setup)
        self.contract_frame.grid(column=0, columnspan=2)

    def get_current_setup_config(self):
        """Retrieve and format the current setup configuration."""
        setup_name = self.initialized_setup.get()
        if not setup_name or setup_name == "None":
            return Invoice.make_contracts_dict(self, 
                                             self.current_file.contracts_sheets,
                                             self.current_file.contracts_activity)

        config = get_offer_contract_data(setup_name)
        return self.format_configuration(config)

    def format_configuration(self, config):
        """Convert raw configuration data to DotDict format."""
        formatted = {}
        for contract_name, settings in config.items():
            if "gd" not in settings:
                settings["gd"] = {"enable": False, "column": "", "amount": 0}
            formatted[contract_name] = DotDict({
                "eb1": settings["earlyBooking1"],
                "eb2": settings["earlyBooking2"],
                "reduc1": settings["reduction1"],
                "reduc2": settings["reduction2"],
                "lt": settings["longTerm"],
                "senior": settings["senior"],
                "combinations": settings["combinations"],
                "gd": settings["gd"],
                "start_date": settings["start_date"],
                "end_date": settings["end_date"],
                "sbi": settings["sbi"]
            })
        return formatted

    def deactivate_table_column(self):
        """Deactivate selected setup in the database."""
        table_name = self.initialized_setup.get()
        if not table_name or table_name == "None":
            return

        with sqlite3.connect('setups.db') as conn:
            cursor = conn.cursor()
            
            # Ensure active_table column exists
            cursor.execute(f"PRAGMA table_info({table_name})")
            if not any(col[1] == 'active_table' for col in cursor.fetchall()):
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN active_table INTEGER DEFAULT 0")
            
            # Deactivate all entries
            cursor.execute(f"UPDATE {table_name} SET active_table = 0")
            conn.commit()

        self.refresh_page(None)

# import tkinter as tk
from tkinter import messagebox

class ContractFrame(tk.Frame):
    """A Tkinter Frame for managing and configuring contract setups."""
    
    def __init__(self, master=None, current_file=None, initialized_setup=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.current_file = current_file
        self.initialized_setup = initialized_setup
        self.entries_dict = {}
        self.active_app = True
        self.new_contract_count = 0  # Track new contracts added via button

        # Initialize max_iter based on current_file or initialized_setup
        if self.current_file:
            self.max_iter = len(self.current_file.statment.columns)
        elif self.initialized_setup:
            self.max_iter = len(self.initialized_setup)
        else:
            self.max_iter = 0  # Default if neither is present

        if not current_file and not self.initialized_setup:
            self.show_file_prompt()
        else:
            self.initialize_contract_interface()

    def show_file_prompt(self):
        """Display file selection prompt."""
        tk.Label(self, text="Please choose a file to make the setup", 
                font=("Helvetica", 24)).grid(row=0, column=0, sticky="w")

    def initialize_contract_interface(self):
        """Initialize main contract configuration interface."""
        # --------------------------
        # Image Loading Section
        # --------------------------
        enable_images = False
        self.load_control_images(enable_images)

        # --------------------------
        # Setup Name Section
        # --------------------------
        self.create_setup_name_field()

        # --------------------------
        # Contract Widgets Section
        # --------------------------
        self.create_contract_widgets()

        self.create_add_button()  # Add the button before submit


        # --------------------------
        # Submission Section
        # --------------------------
        self.create_submit_button()


    def load_control_images(self, enable_images):
        """Load images for control buttons (Up/Down/Delete)."""
        if enable_images:
            image_paths = {
                "Down": r"images\RD.png",
                "Up": r"images\RU.png",
                "Delete": r"images\Delete.png"
            }
            self.control_images = {}
            for name, path in image_paths.items():
                img = Image.open(resource_path(path)).resize((25, 25))
                self.control_images[name] = ImageTk.PhotoImage(img)
                Label(self, image=self.control_images[name]).image = self.control_images[name]  # Keep reference

        else:
            image_paths = {
                "Down": None, 
                "Up": None,
                "Delete": None
            }
            self.control_images = {}
            for name, path in image_paths.items():
                self.control_images[name] = None
            


    def create_setup_name_field(self):
        """Create setup name input field."""
        tk.Label(self, text="Setup name", 
                font=("Helvetica", 10, "underline")).grid(row=1, column=0, sticky="w")
        self.setup_name = tk.Text(self, height=1, width=15)
        self.setup_name.grid(row=2, column=0, sticky="w", padx=5, pady=10)

    def create_contract_widgets(self):
        """Create widgets for each contract."""

        if self.current_file:
            for rank, (contract_name, contract_sheet) in enumerate(self.current_file.contracts_sheets.items(), 1):
                if self.current_file.contracts_activity[contract_name]:
                    self.create_active_contract_widget(contract_name, contract_sheet, rank)
                else:
                    self.show_contract_error(contract_name)

            if not self.active_app:
                messagebox.showwarning("Warning", "Inactive contracts may cause errors")

        elif self.initialized_setup:
            cnt=0
            for contract_name, contract_sheet in self.initialized_setup.items():
                cnt+=1
                #print(contract_sheet.__dict__)
                self.create_active_contract_widget(contract_name, None, cnt)

            if not self.active_app:
                messagebox.showwarning("Warning", "Inactive contracts may cause errors")
            


    def create_add_button(self):
        """Create a button to add new contract widgets."""
        self.add_button = tk.Button(self, text="Add Contract", command=self.add_contract_widget)
        self.add_button.grid(columnspan=2, pady=10)

        # Contract Name Entry
        self.contract_name_label = tk.Label(self, text="Contract Name:")
        self.contract_name_label.grid(columnspan=2, pady=10)
        
        self.contract_name_entry = tk.Entry(self)
        self.contract_name_entry.grid(columnspan=2, pady=10)

    def add_contract_widget(self):
        """Add a new contract widget and increment max_iter."""
        self.max_iter += 1
        self.new_contract_count += 1

        contract_name = self.contract_name_entry.get().strip()
        
        if not contract_name:
            messagebox.showerror("Error", "Contract name cannot be empty!")
        else:
            #base_name = f"New Contract {self.new_contract_count}"
            #unique_name = self.get_unique_name(base_name)
            #print(base_name, unique_name)
            rank = len(self.entries_dict) + 1
            self.initialized_setup[contract_name] = self.initialized_setup["contract"]
            self.create_active_contract_widget(contract_name, None, rank)

    def get_unique_name(self, base_name):
        """Generate unique contract name if duplicates exist"""
        counter = 1
        new_name = base_name
        while new_name in self.entries_dict:
            new_name = f"{base_name} ({counter})"
            counter += 1
        return new_name

    def update_contract_name(self, old_name, new_name):
        """Handle contract name updates from child widgets"""
        if not new_name:
            messagebox.showerror("Error", "Contract name cannot be empty!")
            return False
        if new_name in self.entries_dict:
            messagebox.showerror("Error", "Contract name must be unique!")
            return False
        
        # Update dictionary entry
        widget = self.entries_dict.pop(old_name)
        self.entries_dict[new_name] = widget
        return True

    def create_active_contract_widget(self, contract_name, contract_sheet, rank):
        """Create widget for an active contract using current max_iter."""
        statment_columns = self.current_file.statment.columns if self.current_file else None
        widget = CreateWidgets(
            self,
            contract_name=contract_name,
            contract_sheet=contract_sheet,
            rank=rank,
            max_iter=self.max_iter,  # Use the tracked max_iter
            **self.control_images,
            statment_columns=statment_columns,
            initialized_setup=self.initialized_setup
        )
        self.entries_dict[contract_name] = widget
        widget.grid(pady=20)

    def show_contract_error(self, contract_name):
        """Display error message for inactive contract."""
        tk.Label(self, text=f"{contract_name} has an error", 
                font=("Helvetica", 10, "underline"), fg="red").grid(column=0, sticky="w", padx=5, pady=5)
        self.active_app = False

    def create_submit_button(self):
        """Create submission button."""
        self.submit_button = tk.Button(self, text="Submit", command=self.submit)
        self.submit_button.grid(columnspan=2, pady=10)

    # --------------------------
    # Data Handling Section
    # --------------------------
    def submit(self):
        """Handle submission of contract configuration."""
        setup_name = self.setup_name.get("1.0", "end-1c").strip()
        
        if not self.validate_setup_name(setup_name):
            return

        all_offer_contract_dict = self.collect_contract_data(setup_name)
        self.save_to_database(all_offer_contract_dict)

    def validate_setup_name(self, setup_name):
        """Validate setup name input."""
        if not setup_name:
            tk.Label(self, text="Please enter setup name").grid()
            return False
            
        with sqlite3.connect('setups.db') as conn:
            cursor = conn.cursor()
            existing_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            
        if setup_name in [name[0] for name in existing_tables]:
            tk.Label(self, text="Setup name already exists").grid()
            return False
            
        return True

    def collect_contract_data(self, setup_name):
        """
        Collect configuration data from all contract widgets.
        
        Returns:
            Dictionary containing configuration data for all contracts
        """
        offers_per_contract = {}
        
        for contract_name, widget in self.entries_dict.items():
            entries = widget.get_entries()
            offers = self.process_widget_entries(entries)
            offers_per_contract[contract_name] = offers

        return {setup_name: offers_per_contract}

    def process_widget_entries(self, entries):
        """Process widget entries into structured dictionary."""
        config = {
            "eb1": {"enable": False, "percentage": 0, "date": pd.to_datetime("01/11/2026")},
            "eb2": {"enable": False, "percentage": 0, "date": pd.to_datetime("01/11/2026")},
            "lt": {"enable": False, "percentage": 0, "days": 0},
            "senior": {"enable": False, "column": "", "percentage": 0},
            "reduc1": {"enable": False, "column": "", "percentage": 0},
            "reduc2": {"enable": False, "column": "", "percentage": 0},
            "combinations": {"eb_lt": False, "eb_reduc": False, "eb_senior": False},
            "gd": {"enable": False, "column": "", "amount": 0},
            "start_date": None,
            "end_date": None,
            "sbi": False
        }

        for name, value in entries.items():
            self.update_config(config, name, value)

        return config

    def update_config(self, config, entry_name, value):
        """Update configuration dictionary based on widget entries."""
        category_map = {
            "EB1": "eb1",
            "EB2": "eb2",
            "LT": "lt",
            "Senior": "senior",
            "Reduc1": "reduc1",
            "Reduc2": "reduc2",
            "Combinations": "combinations",
            "GD": "gd"
        }

        for prefix, category in category_map.items():
            if entry_name.startswith(prefix):
                field = entry_name.replace(prefix + " ", "").lower()
                if category == "combinations":
                    config[category][field] = value
                else:
                    config[category][field] = value
                return

        if entry_name == "From date":
            config["start_date"] = value
        elif entry_name == "To date":
            config["end_date"] = value
        elif entry_name == "sbi":
            config["sbi"] = value

    # --------------------------
    # Database Section
    # --------------------------
    def save_to_database(self, all_offer_contract_dict):
        """Save configuration to SQLite database."""
        with sqlite3.connect(resource_path('setups.db')) as conn:
            cursor = conn.cursor()
            
            for setup_name, contracts in all_offer_contract_dict.items():
                self.create_database_table(cursor, setup_name)
                self.insert_contract_data(cursor, setup_name, contracts)
                
            conn.commit()

    def create_database_table(self, cursor, setup_name):
        """Create database table for the setup if not exists."""
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {setup_name}
            (contract_name TEXT PRIMARY KEY,
            offer_name TEXT,
            offer_data TEXT,
            eb1_enable BOOLEAN,
            eb1_percentage REAL,
            eb1_date DATE,
            eb2_enable BOOLEAN,
            eb2_percentage REAL,
            eb2_date DATE,
            reduc1_enable BOOLEAN,
            reduc1_percentage REAL,
            reduc1_column TEXT,
            reduc2_enable BOOLEAN,
            reduc2_percentage REAL,
            reduc2_column TEXT,
            lt_enable BOOLEAN,
            lt_percentage REAL,
            lt_days INTEGER,
            senior_enable BOOLEAN,
            senior_percentage REAL,
            senior_column TEXT,
            combinations_eb_lt BOOLEAN,
            combinations_eb_reduc BOOLEAN,
            combinations_eb_senior BOOLEAN,
            gd_enable BOOLEAN,
            gd_amount REAL,
            gd_column TEXT,
            start_date DATE,
            end_date DATE,
            sbi BOOLEAN,
            active_table INTEGER DEFAULT 1)''')

    def insert_contract_data(self, cursor, setup_name, contracts):
        """Insert contract data into database."""
        for contract_name, data in contracts.items():
            cursor.execute(f'''
                INSERT INTO {setup_name} (
                    offer_name, contract_name, offer_data,
                    eb1_enable, eb1_percentage, eb1_date,
                    eb2_enable, eb2_percentage, eb2_date,
                    reduc1_enable, reduc1_percentage, reduc1_column,
                    reduc2_enable, reduc2_percentage, reduc2_column,
                    lt_enable, lt_percentage, lt_days,
                    senior_enable, senior_percentage, senior_column,
                    combinations_eb_lt, combinations_eb_reduc, combinations_eb_senior,
                    gd_enable, gd_amount, gd_column,
                    start_date, end_date, sbi, active_table
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                self.generate_db_parameters(setup_name, contract_name, data))

    def generate_db_parameters(self, setup_name, contract_name, data):
        """Generate database parameters from contract data."""
        return (
            setup_name, contract_name, str(data),
            data["eb1"]["enable"], data["eb1"]["percentage"], data["eb1"]["date"],
            data["eb2"]["enable"], data["eb2"]["percentage"], data["eb2"]["date"],
            data["reduc1"]["enable"], data["reduc1"]["percentage"], data["reduc1"]["column"],
            data["reduc2"]["enable"], data["reduc2"]["percentage"], data["reduc2"]["column"],
            data["lt"]["enable"], data["lt"]["percentage"], data["lt"]["days"],
            data["senior"]["enable"], data["senior"]["percentage"], data["senior"]["column"],
            data["combinations"]["eb_lt"], data["combinations"]["eb_reduc"], data["combinations"]["eb_senior"],
            data["gd"]["enable"], data["gd"]["amount"], data["gd"]["column"],
            data["start_date"], data["end_date"], data["sbi"], 1
        )
        

class CreateWidgets(tk.Frame):
    def __init__(self, master, contract_name, contract_sheet, rank, max_iter, Down, Up, Delete, statment_columns, initialized_setup):
        super().__init__(master)
        self.contract_name = contract_name  # Store original name
        self.rank = rank
        self.entries = {}
        self.labels = ["EB1 Enable", "EB1 Percentage", "EB1 Date",
                    "EB2 Enable", "EB2 Percentage", "EB2 Date",
                    "LT Enable", "LT Percentage", "LT Days",
                    "Reduc1 Enable", "Reduc1 Column", "Reduc1 Percentage",
                    "Reduc2 Enable", "Reduc2 Column", "Reduc2 Percentage",
                    "Senior Enable", "Senior Column", "Senior Percentage",
                    "Combinations EB_LT", "Combinations EB_Reduc", "Combinations EB_Senior",
                    "GD Enable", "GD Column", "GD amount",
                    "From date", "To date", "sbi"]
        self.initialized_setup = initialized_setup
        self.create_widgets(contract_name, contract_sheet, rank, max_iter, Down, Up, Delete, statment_columns)
        self.configure(highlightbackground="black", highlightthickness=2)
        #print(self.initialized_setup)

    def create_widgets(self, contract_name, contract_sheet, rank, max_iter, Down, Up, Delete, statment_columns):
        self.create_entries(contract_sheet, contract_name)
        if Down:
            self.place_navigation_buttons(rank, max_iter, Down, Up, Delete, contract_name)
        self.place_labels(contract_name)
        self.place_additional_widgets(contract_name, contract_sheet, rank, max_iter, Down, Up, Delete, statment_columns)

    def create_entries(self, contract_sheet, contract_name):
        if contract_name in self.initialized_setup:
            self.contract_setup = self.initialized_setup[contract_name]
            #for label in self.labels:
                #if "enable" in label.lower():
                    #self.entries[label] = tk.BooleanVar()
                #elif "From date" in label or "To date" in label or "date" in label.lower():
                    #self.entries[label] = DateEntry(self, date_pattern="dd/mm/yyyy")
                    #if "From date" in label:
                        #self.entries[label].set_date(contract_sheet.loc[0, "first date"])
                    #elif "To date" in label:
                        #self.entries[label].set_date(contract_sheet.loc[len(contract_sheet) - 1, "second date"])
                    #else:
                        #self.entries[label].set_date(contract_sheet.loc[0, "first date"])
                #elif "percentage" in label.lower() or "amount" in label.lower() or "days" in label.lower():
                    #self.entries[label] = tk.Entry(self)
                    
                
            
            self.entries["EB1 Enable"] = tk.BooleanVar(value=self.contract_setup.eb1['enable'])
            self.entries["EB1 Percentage"] = tk.Entry(self)
            self.entries["EB1 Percentage"].delete(0,tk.END)
            self.entries["EB1 Percentage"].insert(0,self.contract_setup.eb1["percentage"])
            self.entries["EB1 Date"] = DateEntry(self)
            self.entries["EB1 Date"].set_date(self.contract_setup.eb1['date'])

            self.entries["EB2 Enable"] = tk.BooleanVar(value=self.contract_setup.eb2['enable'])
            self.entries["EB2 Percentage"] = tk.Entry(self)
            self.entries["EB2 Percentage"].delete(0,tk.END)
            self.entries["EB2 Percentage"].insert(0,self.contract_setup.eb2["percentage"])
            self.entries["EB2 Date"] = DateEntry(self)
            self.entries["EB2 Date"].set_date(self.contract_setup.eb2['date'])

            self.entries["LT Enable"] = tk.BooleanVar(value=self.contract_setup.lt['enable'])
            self.entries["LT Percentage"] = tk.Entry(self)
            self.entries["LT Percentage"].delete(0,tk.END)
            self.entries["LT Percentage"].insert(0,self.contract_setup.lt["percentage"])
            self.entries["LT Days"] = tk.Entry(self)
            self.entries["LT Days"].delete(0,tk.END)
            self.entries["LT Days"].insert(0,self.contract_setup.lt['days'])

            self.entries["Reduc1 Enable"] = tk.BooleanVar(value=self.contract_setup.reduc1['enable'])
            self.entries["Reduc1 Percentage"] = tk.Entry(self)
            self.entries["Reduc1 Percentage"].delete(0,tk.END)
            self.entries["Reduc1 Percentage"].insert(0,self.contract_setup.reduc1["percentage"])

            self.entries["Reduc2 Enable"] = tk.BooleanVar(value=self.contract_setup.reduc2['enable'])
            

            self.entries["Reduc2 Percentage"] = tk.Entry(self)
            self.entries["Reduc2 Percentage"].delete(0,tk.END)
            self.entries["Reduc2 Percentage"].insert(0,self.contract_setup.reduc2["percentage"])

            self.entries["Senior Enable"] = tk.BooleanVar(value=self.contract_setup.senior['enable'])
            self.entries["Senior Percentage"] = tk.Entry(self)
            self.entries["Senior Percentage"].delete(0,tk.END)
            self.entries["Senior Percentage"].insert(0,self.contract_setup.senior["percentage"])

            self.entries["Combinations EB_LT"] = tk.IntVar(value=self.contract_setup.combinations['eb_lt'])
            self.entries["Combinations EB_Reduc"] = tk.IntVar(value=self.contract_setup.combinations['eb_reduc'])
            self.entries["Combinations EB_Senior"] = tk.IntVar(value=self.contract_setup.combinations['eb_senior'])

            self.entries["GD Enable"] = tk.BooleanVar(value=self.contract_setup.gd['enable'])
            self.entries["GD Amount"] = tk.Entry(self)
            self.entries["GD Amount"].delete(0,tk.END)
            self.entries["GD Amount"].insert(0,self.contract_setup.gd["amount"])

            self.entries["From date"] = DateEntry(self)
            self.entries["From date"].set_date(self.contract_setup.start_date)

            self.entries["To date"] = DateEntry(self)
            self.entries["To date"].set_date(self.contract_setup.end_date)

            self.entries["sbi"] = tk.BooleanVar(value=self.contract_setup.sbi)


    def place_navigation_buttons(self, rank, max_iter, Down, Up, Delete, contract_name):
        if rank != 1:
            tk.Button(self, image=Up).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        if rank != max_iter:
            tk.Button(self, image=Down).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        tk.Button(self, image=Delete).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        tk.Label(self, text=str(rank) + "-" + contract_name, font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Label(self, text="").grid(row=1, column=0, sticky="w", padx=5, pady=5)

    def place_labels(self, contract_name):
        if contract_name != "contract":
            tk.Label(self, text="From", font=("Helvetica", 10, "underline")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.entries["From date"].grid(row=2, column=1, sticky="w", padx=5, pady=5)
            tk.Label(self, text="To", font=("Helvetica", 10, "underline")).grid(row=2, column=2, sticky="w", padx=5, pady=5)
            self.entries["To date"].grid(row=2, column=3, sticky="w", padx=5, pady=5)
        tk.Label(self, text="").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Early Booking 1", font=("Helvetica", 10, "underline")).grid(row=4, column=0, sticky="w", padx=5, pady=5)

        # eb1

    def place_additional_widgets(self,contract_name, contract_sheet, rank, max_iter, Down, Up, Delete, statment_columns):

        # Replace the label with editable entry for contract name
        name_frame = tk.Frame(self)
        name_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Rank label (static)
        tk.Label(name_frame, text=f"{rank}-", font=("Helvetica", 12)).pack(side="left")

        if rank != 1:
            tk.Button(self, image=Up).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        if rank != max_iter:   
            tk.Button(self, image=Down).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        is_sheets_setup = True if isinstance(contract_sheet, pd.DataFrame) else False
        tk.Button(self, image=Delete).grid(row=0, column=4, sticky="w", padx=5, pady=5)

        tk.Label(self, text=str(rank) + "-" + contract_name, font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Label(self, text="").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        if contract_name != "contract":
            tk.Label(self, text="From", font=("Helvetica", 10, "underline")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.entries["From date"].grid(row=2, column=1, sticky="w", padx=5, pady=5)
            tk.Label(self, text="To", font=("Helvetica", 10, "underline")).grid(row=2, column=2, sticky="w", padx=5, pady=5)
            self.entries["To date"].grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        # eb2
        eb1_start_row = 4
        tk.Label(self, text="Early Booking 1", font=("Helvetica", 10, "underline")).grid(row=eb1_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=eb1_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["EB1 Enable"]).grid(row=eb1_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Early booking percentage").grid(row=eb1_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["EB1 Percentage"].grid(row=eb1_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Early booking date").grid(row=eb1_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["EB1 Date"].grid(row=eb1_start_row + 2, column=3, sticky="w", padx=5, pady=5)
        tk.Label(self, text="").grid(row=eb1_start_row + 3, column=0, sticky="w", padx=5, pady=5)

        # eb2
        eb2_start_row = 8
        tk.Label(self, text="Early Booking 2", font=("Helvetica", 10, "underline")).grid(row=eb2_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=eb2_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["EB2 Enable"]).grid(row=eb2_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Early booking percentage").grid(row=eb2_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["EB2 Percentage"].grid(row=eb2_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Early booking date").grid(row=eb2_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["EB2 Date"].grid(row=eb2_start_row + 2, column=3, sticky="w", padx=5, pady=5)
        tk.Label(self, text="").grid(row=eb2_start_row + 3, column=0, sticky="w", padx=5, pady=5)

        # Reduction 1
        reduc1_start_row = 12
        tk.Label(self, text="Reduction 1", font=("Helvetica", 10, "underline")).grid(row=reduc1_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=reduc1_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Reduc1 Enable"]).grid(row=reduc1_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Reduction 1 percentage").grid(row=reduc1_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["Reduc1 Percentage"].grid(row=reduc1_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Reduction 1 column").grid(row=reduc1_start_row + 2, column=2, sticky="w", padx=5, pady=5)

        self.entries["Reduc1 Column"] = ttk.Combobox(self, values=list(statment_columns)) if is_sheets_setup else tk.Entry(self)
        self.entries["Reduc1 Column"].set(self.contract_setup.reduc1['column']) if is_sheets_setup else None
        self.entries["Reduc1 Column"].grid(row=reduc1_start_row + 2, column=3)

        # Reduction 2
        reduc2_start_row = 15
        tk.Label(self, text="Reduction 2", font=("Helvetica", 10, "underline")).grid(row=reduc2_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=reduc2_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Reduc2 Enable"]).grid(row=reduc2_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Reduction 2 percentage").grid(row=reduc2_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["Reduc2 Percentage"].grid(row=reduc2_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Reduction 2 column").grid(row=reduc2_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["Reduc2 Column"] = ttk.Combobox(self, values=list(statment_columns)) if is_sheets_setup else tk.Entry(self)
        self.entries["Reduc2 Column"].set(self.contract_setup.reduc2['column']) if is_sheets_setup else None
        self.entries["Reduc2 Column"].grid(row=reduc2_start_row + 2, column=3)

        # Long term
        lt_start_row = 18
        tk.Label(self, text="Long term", font=("Helvetica", 10, "underline")).grid(row=lt_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=lt_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["LT Enable"]).grid(row=lt_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Long term percentage").grid(row=lt_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["LT Percentage"].grid(row=lt_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Long term days").grid(row=lt_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["LT Days"].grid(row=lt_start_row + 2, column=3, sticky="w", padx=5, pady=5)


        # Senior
        senior_start_row = 21
        tk.Label(self, text="Senior", font=("Helvetica", 10, "underline")).grid(row=senior_start_row, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Enable").grid(row=senior_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Senior Enable"]).grid(row=senior_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Senior percentage").grid(row=senior_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        self.entries["Senior Percentage"].grid(row=senior_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Senior column").grid(row=senior_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["Senior Column"] = ttk.Combobox(self, values=list(statment_columns)) if is_sheets_setup else tk.Entry(self)
        self.entries["Senior Column"].set(self.contract_setup.senior['column']) if is_sheets_setup else None
        self.entries["Senior Column"].grid(row=senior_start_row + 2, column=3)

        # Combinations
        combinations_start_row = 24
        tk.Label(self, text="Combinations", font=("Helvetica", 10, "underline")).grid(row=combinations_start_row, column=0, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Early booking with long term").grid(row=combinations_start_row + 1, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Combinations EB_LT"]).grid(row=combinations_start_row + 1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Early booking with reduction").grid(row=combinations_start_row + 2, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Combinations EB_Reduc"]).grid(row=combinations_start_row + 2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Early booking with senior").grid(row=combinations_start_row + 3, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["Combinations EB_Senior"]).grid(row=combinations_start_row + 3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(self, text="Spo by arrival").grid(row=combinations_start_row + 4, column=0, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["sbi"]).grid(row=combinations_start_row + 4, column=1, sticky="w", padx=5, pady=5)


        # New Year Galadinner 
        tk.Label(self, text="New Year Galadinner", font=("Helvetica", 10, "underline")).grid(row=combinations_start_row, column=2, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Enable New Year Galadinner").grid(row=combinations_start_row + 1, column=2, sticky="w", padx=5, pady=5)
        tk.Checkbutton(self, variable=self.entries["GD Enable"]).grid(row=combinations_start_row + 1, column=3, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Galadinner Amount").grid(row=combinations_start_row + 2, column=2, sticky="w", padx=5, pady=5)
        self.entries["GD Amount"].grid(row=combinations_start_row + 2, column=3, sticky="w", padx=5, pady=5)
        
        tk.Label(self, text="Galadinner column").grid(row=combinations_start_row + 3, column=2, sticky="w", padx=5, pady=5)
        self.entries["GD Column"] = ttk.Combobox(self, values=list(statment_columns)) if is_sheets_setup else tk.Entry(self)
        self.entries["GD Column"].set(self.contract_setup.gd['column']) if is_sheets_setup else None
        self.entries["GD Column"].grid(row=combinations_start_row + 3, column=3)


    def get_entries(self):
        updated_entries = {}
        for key, entry in self.entries.items():
            if isinstance(entry, tk.BooleanVar):
                updated_entries[key] = entry.get()  # For BooleanVar
            elif isinstance(entry, DateEntry):
                updated_entries[key] = entry.get()  # Assuming DateEntry has a get() method
            else:
                updated_entries[key] = entry.get()  # For other types of entries like Entry or Combobox
        return updated_entries

    def update_contract_name(self, event):
        new_name = self.name_entry.get().strip()
        if new_name and new_name != self.contract_name:
            # Notify parent frame to handle the name change
            success = self.master.update_contract_name(self.contract_name, new_name)
            if success:
                self.contract_name = new_name
            else:
                # Revert to previous name if invalid
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.contract_name)
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################








class Apply(ttk.Frame):
    def __init__(self,parent, current_file=None):
        super().__init__(parent)
        self.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(self, background="red", scrollregion=(0,0,self.winfo_width(),20000))
        self.canvas.pack(expand=True, fill='both')

        self.apply_setup = ApplySetup(self)
        # self.canvas.create_window((-1,0), window = self.ApplySetup, anchor='nw', width=self.winfo_width(), height=20000)
        

        self.scrollbar = ttk.Scrollbar(self, orient= "vertical",command=self.canvas.yview)
        self.scrollbar.place(relx=1,rely=0,relheight=1,anchor='ne')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # events
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(-int(event.delta / 60),'units'))
        self.bind('<Configure>', self.update_size)

    def update_size(self, event):
        self.canvas.create_window((-1,0), window = self.apply_setup, anchor='nw', width=self.winfo_width(), height=20000)




class ApplySetup(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)


        self.pack(expand=True,fill='both')
        
        if not container:
            
            tk.Label(self, text="Please choose a file to make the setup", font=("Helvetica", 24)).grid(row=0, column=0, sticky="w", padx=0, pady=0)

        else:
            
            self.tables = get_tables()
            
            tk.Label(self, text="File name", font=("Helvetica", 14,)).grid(row=0, column=0, sticky="w", padx=0, pady=0)
            
            self.file_setup_dict = {}
            self.setup_box = {}
            for file_index in range(len(container)):
                tk.Label(self, text=container[file_index].filename, font=("Helvetica", 10, "underline")).grid(row=1+file_index, column=0, sticky="w", padx=0, pady=0)
                self.setup_box[container[file_index]] = ttk.Combobox(self, values=list(self.tables.keys()))
                self.setup_box[container[file_index]].grid(row=1+file_index, column=1, sticky="w", padx=0, pady=0)
                

            # Button
            self.submit_button = tk.Button(self, text="Submit", command=self.submit)
            self.submit_button.grid(columnspan=2, pady=10)

    def format_table_data(self, table_data):
        # Calculate the maximum width for each column
        column_widths = {
            col: max(len(str(col)), max(table_data[col].astype(str).map(len)))
            for col in table_data.columns
        }
        
        # Format headers (centered)
        headers = "  ".join(
            f"{col:^{column_widths[col]}}" for col in table_data.columns
        )
        
        # Format rows (centered)
        rows = "\n".join(
            "    ".join(
                f"{str(value):^{column_widths[col]}}" for col, value in row.items()
            )
            for row in table_data.to_dict(orient="records")
        )
        
        # Combine headers and rows
        return f"{headers}\n{rows}"

    def submit(self):
        for file, setup in self.setup_box.items():

            offers_dict = {}

            statment = file.statment
            contracts_sheets = file.contracts_sheets

            if len(setup.get()) == 0:
                
                for contract_name, contract_data in file.contracts_sheets.items():
                    offers_dict[contract_name] = Contract(contract_name,contract_data,file.contracts_activity[contract_name])
                    
            else:
                self.values = get_offer_contract_data(setup.get())
                
                for contract_name, contract_data in file.contracts_sheets.items():
                    offers_dict[contract_name] = Contract(contract_name,contract_data,file.contracts_activity[contract_name],self.values[contract_name]["senior"],self.values[contract_name]["earlyBooking1"],self.values[contract_name]["earlyBooking2"],self.values[contract_name]["longTerm"],self.values[contract_name]["reduction1"],self.values[contract_name]["reduction2"],self.values[contract_name]["combinations"], self.values[contract_name]["gd"],self.values[contract_name]["start_date"],self.values[contract_name]["end_date"])

            invoice = Invoice(file,offers_dict)
            prices = invoice.prices
            date_prices = invoice.Index_contract_date_range_dict

            statment = invoice.output_statment
            output_folder = "output"
            # Create the output folder if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Path to the output file
            output_file_path = os.path.join(output_folder, f"{file.filename}_output.xlsx")


            statment.loc[prices.keys(), "Total price"] = [round(price, 2) for price in list(prices.values())]
            
            
            for date in date_prices.keys():
                
                prices = date_prices[date]
                    
                result = ""
                for table_name, table_data in prices.items():
                    # Convert to datetime if necessary
                    table_data['first date'] = pd.to_datetime(table_data['first date'])
                    table_data['second date'] = pd.to_datetime(table_data['second date'])

                    # Format to only show date
                    table_data['first date'] = table_data['first date'].dt.date
                    table_data['second date'] = table_data['second date'].dt.date

                    formatted_table = self.format_table_data(table_data)
                    result += f"{table_name}:\n{formatted_table}\n\n"
                    
                statment.loc[date, "calculations"] = result
                
            if "Amount-hotel" in statment.columns:
                statment["Difference"] = statment["Total price"] - statment["Amount-hotel"]
                
                DifferenceTable(self, statment, file.filename).grid()
            
            # cols_to_drop = statment.columns[~(statment != 0).any()]
            # columns_to_keep = ['Difference']
            # # Drop the selected columns, creating a new DataFrame
            # statment_filtered = statment.drop(columns=list(set(cols_to_drop) - set(columns_to_keep)), inplace=True)

            #statment.to_excel(output_file_path, index=False)
            filename_without_ext = os.path.splitext(file.filename)[0]
            output_path = f"output/{filename_without_ext}_output.xlsx"

            # Check if the file exists and delete it
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"Old file '{output_path}' deleted.")

            columns_to_check = ["Res_date", "Arrival", "Departure", "date_check"]

            for col in columns_to_check:
                if col in statment.columns:
                    statment[col] = pd.to_datetime(statment[col]).dt.date  # Keeps only the date part

            # Now, call the function to create the new file# Columns to remove if they exist
            columns_to_remove = {"senior", "longTerm", "Reduction1", "Reduction2", "earlyBooking1", "earlyBooking2", "date_check", "activity"}
            statment = statment.drop(columns=[col for col in columns_to_remove if col in statment], errors='ignore')

            # Reorder columns to place "Amount-hotel" and "Total price" just before "Difference"
            cols = list(statment.columns)

            if "Amount-hotel" in cols and "Total price" in cols and "Difference" in cols:
                cols.remove("Amount-hotel")
                cols.remove("Total price")
                cols.insert(cols.index("Difference"), "Amount-hotel")  # Insert before "Difference"
                cols.insert(cols.index("Difference"), "Total price")   # Insert before "Difference"

            statment = statment[cols]
            # Check if 'difference' column exists before modifying
            if 'Difference' in statment.columns:
                statment.loc[np.abs(statment['Difference']) < 0.5, 'Difference'] = 0

            if "Booking No." in statment.columns:
                statment['Booking No.'] = statment['Booking No.'].apply(lambda x: int(x))

            FormatExcel(statment, output_path)

def get_tables():
    db_file = 'setups.db'
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Create a dictionary to store tables and their values
        tables_and_values = {}

        # Iterate over each table
        for table in tables:
            table_name = table[0]

            # Check if the table has the 'active_table' column
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            if 'active_table' not in column_names:
                # If 'active_table' column doesn't exist, add it with default value 1
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN active_table INTEGER DEFAULT 1;")
                conn.commit()

            # Fetch all rows from the table
            cursor.execute(f"SELECT * FROM {table_name} WHERE active_table = 1;")
            rows = cursor.fetchall()
            # Store the rows in the dictionary
            if rows:
                tables_and_values[table_name] = rows

        # Close the database connection
        conn.close()

        return tables_and_values

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None



def get_offer_contract_data(offer_name):
    conn = sqlite3.connect('setups.db')  # Update 'setups.db' with your actual database name
    c = conn.cursor()
    
    c.execute(f"SELECT * FROM {offer_name}")
    rows = c.fetchall()
    offer_contract_data = {}
    for row in rows:
        contract_data = {}
        contract_data["contract_name"] = row[0]
        contract_data["offer_name"] = row[1]
        contract_data["offer_data"] = row[2]
        
        eb1 = {"enable": row[3], "percentage": row[4], "date": parse_date(row[5])}
        eb2 = {"enable": row[6], "percentage": row[7], "date": parse_date(row[8])}
        reduc1 = {"enable": row[9], "percentage": row[10], "column": row[11]}
        reduc2 = {"enable": row[12], "percentage": row[13], "column": row[14]}
        lt = {"enable": row[15], "percentage": row[16], "days": row[17]}
        senior = {"enable": row[18], "percentage": row[19], "column": row[20]}
        combinations = {"eb_lt": row[21], "eb_reduc": row[22], "eb_senior": row[23]}
        if len(row) >=30:
            gd = {"enable": row[24], "amount": row[25], "column": row[26]}
            start_date = parse_date(row[27])
            end_date = parse_date(row[28])
            sbi = row[29]
            active = row[30]
        else:
            gd = {"enable": 0, "amount": 0, "column": ""}
            start_date = parse_date(row[24])
            end_date = parse_date(row[25])
            sbi = row[26]
            active = row[27]
            
        
        contract_data["earlyBooking1"] = eb1
        contract_data["earlyBooking2"] = eb2
        contract_data["reduction1"] = reduc1
        contract_data["reduction2"] = reduc2
        contract_data["longTerm"] = lt
        contract_data["senior"] = senior
        contract_data["combinations"] = combinations
        contract_data["gd"] = gd
        contract_data["start_date"] = start_date
        contract_data["end_date"] = end_date
        contract_data["active"] = active
        contract_data["sbi"] = sbi

        offer_contract_data[contract_data['contract_name']] = contract_data

    conn.close()
    return offer_contract_data


def parse_date(date_string):
    if date_string:
        # Define a list of possible date formats
        date_formats = [
            '%m/%d/%y', '%m-%d-%y', '%Y-%m-%d', '%d-%m-%Y',  # Various common formats
            '%m/%d/%Y', '%m-%d-%Y', '%d-%m-%y', '%d/%m/%y',  # More variations
            '%b %d, %Y', '%B %d, %Y',  # Month name abbreviations and full names
            '%b %d %Y', '%B %d %Y', '%b. %d, %Y', '%B. %d, %Y',  # With or without dots after month abbreviation
            '%d %b %Y', '%d %B %Y',  # Day and month swapped
            '%Y/%m/%d', '%Y-%m-%d %H:%M:%S'  # ISO format with or without time
        ]

        # Try to match the date string with the regular expressions for the defined formats
        for date_format in date_formats:
            try:
                parsed_date = pd.to_datetime(date_string, format=date_format)
                return parsed_date
            except ValueError:
                continue

        # If none of the formats matched, return None or handle the case as per your requirement
        return None
    return None








############################################################################
############################################################################
############################################################################
############################################################################

class DifferenceTable(ttk.Frame):
    def __init__(self,parent, statment, filename):
        super().__init__(parent)

        # Make a copy to avoid modifying the original dataframe
        statment = statment.copy()

        # Format 'Invoice No.' as integer if present
        if "Invoice No." in statment.columns:
            statment["Invoice No."] = statment["Invoice No."].astype("Int64")

        # Format 'Difference' column to avoid scientific notation
        if "Difference" in statment.columns:
            statment["Difference"] = statment["Difference"].apply(lambda x: f"{x:.2f}")
        columns_to_review = ["Amount-hotel","Total price","Difference"]
        if "Invoice No." in statment:
            columns_to_review.append("Invoice No.")

        elif "Folio" in statment:
            columns_to_review.append("Folio")

        difference_table = statment[statment['Difference'] != "0.00"][columns_to_review]
        
        tk.Label(self, text=filename, font=("Helvetica", 10, "underline"))
        
        # Create a Table object
        table = Table(self, dataframe=difference_table)

        # Optionally, customize table appearance (e.g., column widths, font)
        table.show()

        
if __name__ == "__main__":
    global container
    container = [FileUploader("test files\des siva makadi.xlsx")]
    root = tk.Tk()
    root.geometry("800x600")
    app = SetupContract(root)
    root.mainloop()
