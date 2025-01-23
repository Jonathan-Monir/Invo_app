import pandas as pd
import openpyxl

import pandas as pd
import numpy as np
from contract import Contract
import warnings
import os

# Clear the terminal

warnings.filterwarnings("ignore", message="A value is trying to be set on a copy of a slice from a DataFrame.*")


class FileUploader:
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = filepath.split('/')[-1]
        
        self.fixed_file = self.fix_file()
        self.statment = self.fixed_file[0]
        self.contracts_sheets = self.fixed_file[1]
        self.contracts_activity = self.fixed_file[2]
        self.num_rows = self.statment.shape[1]

    def to_df(self):
        # convert to excel
        excel_data = pd.read_excel(self.filepath, sheet_name=None)

        return excel_data

    def fix_empty(self, df, column):
        # get df that has empty rows
        df.loc[(df[column].isnull() | (df[column] == '')),column] = np.nan

        # get rows with nulls
        empty_rows = df[column].isna()
        
        # set activity of rows to 0
        df.loc[empty_rows, "activity"] = 0
        if "error_type" in df.columns:
            # type error in error type column
            if not df.loc[empty_rows, "error_type"].empty:
                df.loc[empty_rows, "error_type"] += f", empty in {column}"
            else:
                df.loc[empty_rows, "error_type"] = f"empty in {column}"
        return df

    def fix_date(self, df_date_fix, column):
        # Detect and parse date format dynamically
        try_formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%m-%d-%Y', '%Y-%d-%m', '%d-%m-%Y']
        df_date_fix["date_check"] = pd.NA

        def remove_dot(value):
            if '.' in value:
                return value.split('.')[0]
            else:
                return value
                
        for date_format in try_formats:
            try:
                df_date_fix.loc[df_date_fix['date_check'].isna(), 'date_check'] = pd.to_datetime(df_date_fix[column], errors="coerce", format=date_format)
                

                
            except ValueError:
                pass
        df_date_fix["date_check"] = pd.to_datetime(df_date_fix["date_check"])
        # Extract components and format desired output
        df_date_fix["day"] = df_date_fix["date_check"].dt.strftime('%d')
        df_date_fix["month"] = df_date_fix["date_check"].dt.strftime('%m')  # Numeric month format
        df_date_fix["year"] = df_date_fix["date_check"].dt.strftime('%Y') 
    
   
        # Combine and format as "MM/DD/YYYY"
        df_date_fix[column] = df_date_fix[["month", "day", "year"]].apply(
            lambda row: f"{row['month']}/{row['day']}/{row['year']}", axis=1
        )

        # Set "activity" to 0 for rows with date errors
        error_rows = df_date_fix["date_check"].isna()
        df_date_fix.loc[error_rows, "activity"] = 0

        
        # Update error_type if applicable
        if "error_type" in df_date_fix.columns:
            if not df_date_fix.loc[error_rows, "error_type"].empty:
                df_date_fix.loc[error_rows, "error_type"] += f", Date error in {column}"
            else:
                df_date_fix.loc[error_rows, "error_type"] = f"Date error in {column}"

        df_date_fix.drop("day", axis=1, inplace=True)
        df_date_fix.drop("month", axis=1, inplace=True)
        df_date_fix.drop("year", axis=1, inplace=True)
        
        df_date_fix[column] = pd.to_datetime(df_date_fix[column], errors="coerce")
        
        
        return df_date_fix

    def fix_numbers(self, statment_fix, columns_to_fix):
        for column in columns_to_fix:
            try:
                statment_fix["numeric_check"] = pd.to_numeric(statment_fix[column])
            except ValueError:
                # Identify rows with numeric errors and set "activity" to 0
                error_rows = pd.to_numeric(statment_fix[column], errors="coerce").isna()
                statment_fix.loc[error_rows, "activity"] = 0

                # Append the error_type with the column name
                if "error_type" in statment_fix.columns:
                    statment_fix.loc[error_rows, "error_type"] += f", Numeric error in {column}"
                else:
                    statment_fix.loc[error_rows, "error_type"] = f"Numeric error in {column}"
            
            statment_fix.drop("date_check", axis = 1, inplace = True)

        return statment_fix

    def fix_overlap(self, df, contracts_activity):
        dictionary_items = df.copy().items()

        for sheet_name, sheet_data in dictionary_items:
            
            if not(contracts_activity[sheet_name]):
                continue
            
            last_fixed_index = 0
            part = 0
            overlap = False
            
            if sheet_name != "statment":
                for row_index in range(len(sheet_data['second date'])-1):
                    
                    if pd.isna(sheet_data['second date'].iloc[row_index] - sheet_data['first date'][row_index+1]):
                        continue
                    if abs(sheet_data['second date'].iloc[row_index] - sheet_data['first date'][row_index+1]).days > 1:
                        overlap = True
                        df[sheet_name + " part: "+ str(part)] = sheet_data.iloc[last_fixed_index:row_index+1,:]
                        last_fixed_index = row_index + 1
                        part += 1
                if overlap:
                    df[sheet_name + " part: "+ str(part)] = sheet_data.iloc[last_fixed_index:]
                    del df[sheet_name]
        
        return df
    
    def check_statment(self, statment):

        if "Arrival" not in statment.iloc[0] or "Departure" not in statment.iloc[0]:

            # Identify the row where the column names are located
            header_row = statment[statment.apply(lambda row: row.notnull().all(), axis=1)].index[0]

            # Use the identified row as the header
            statment.columns = statment.iloc[header_row]
            statment = statment.drop(header_row)

            # Drop the null rows and reset the index
            statment = statment.dropna().reset_index(drop=True)
        
        statment = self.fix_empty(statment, "Rate code")

        columns_dates_to_fix = ["Arrival","Departure"]

        if "Res_date" in statment:
            columns_dates_to_fix.append("Res_date")

        for column in columns_dates_to_fix:
            statment = self.fix_date(statment, column)

        # columns_numeric_to_fix = ["Amount-hotel","Currency rate","Departure"]
        # statment = self.fix_numbers(statment, columns_numeric_to_fix)
        
        return self.initialize_offers(statment)

    def check_contract(self, sheets):
        contracts = {}
        contracts_activity = dict()

        for sheet_name, sheet_data in sheets.items():
            if sheet_name != "statment":
                
                columns_dates_to_fix = ["first date","second date"]
                for column in columns_dates_to_fix:
                    contract = self.fix_date(sheet_data, column)
                
                
                for index, row in contract.iterrows():
                    if row['first date'] > row['second date']:
                        contract.at[index, 'error_type'] = f"First date greater than second date"
                        contract.at[index, 'activity'] = False
                
                contract.dropna(subset=['first date', 'second date'], inplace=True)
                
                    
                active = ~(contract["activity"] == 0).any()
                
                contracts[sheet_name], contracts_activity[sheet_name] = contract, active
        
        contracts = self.fix_overlap(contracts,contracts_activity)
        
        # fixed_contracts = {k: contracts[k] for k in contracts if k != "contract"}
        # fixed_contracts["contract"] = contracts["contract"]
        return contracts, contracts_activity
    
    def initialize_offers(self,statment):
        statment["earlyBooking1"] = 0
        statment["earlyBooking2"] = 0
        statment["senior"] = 0
        statment["longTerm"] = 0
        statment["Reduction1"] = 0
        statment["Reduction2"] = 0
        
        if "Res_date" not in statment.columns:
            statment["Res_date"] = statment["Arrival"]
        return statment

        
    def fix_file(self):
        
        sheets = self.to_df()
        
        sheets["statment"]["activity"] = 1
        sheets["statment"]["error_type"] = ""


        for sheet_name, sheet_data in sheets.items():
            sheets[sheet_name] = sheet_data.dropna(axis=1, how="all")
            sheets[sheet_name]["activity"] = 1
            sheets[sheet_name]["error_type"] = ""

        sheets["statment"] = self.check_statment(sheets["statment"])
        statment = sheets["statment"]

        contracts_activity = {sheet_name: 1 for sheet_name, sheet_data in sheets.items() if sheet_name != "statment"}
        
        contracts_sheets, contracts_activity = self.check_contract(sheets)
        
        return statment, contracts_sheets, contracts_activity

    
if __name__ == "__main__":
    file = FileUploader(r"test files\Biblio- Resort 23-24 . Invo.xlsx")
    statment, contracts_sheets, contracts_activity = file.fix_file()
    print(statment)
