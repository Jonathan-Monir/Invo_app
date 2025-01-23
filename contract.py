import pandas as pd

# To Do: 
class Contract:
    eb1 = {"enable":False,"percentage":0,"date":pd.to_datetime("01/11/2026")}
    eb2 = {"enable":False,"percentage":0,"date":pd.to_datetime("01/11/2026")}
    lt = {"enable":False,"percentage":0,"days":0}
    senior = {"enable":False,"column":"","percentage":0}
    reduc1 = {"enable":False,"column":"","percentage":0}
    reduc2 = {"enable":False,"column":"","percentage":0}
    extra = {"enable":False,"amount":0}
    combinations = {"eb_lt":False,"eb_reduc":False,"eb_senior":False}
    gd = {"enable":False,"column":"","amount":0}
    sbi = False
    
    def __init__(self, contract_name, contract_sheet, activity, Senior=senior, EarlyBooking1=eb1, EarlyBooking2=eb2, LongTerm=lt, Reduction1=reduc1, Reduction2=reduc2, combinations=combinations, GalaDinner=gd, start_date=None, end_date=None, sbi=sbi):
        


        self.contract_name = contract_name
        self.contract_sheet = contract_sheet
        self.EarlyBooking1 = EarlyBooking1
        self.Senior = Senior
        self.EarlyBooking2 = EarlyBooking2
        self.LongTerm = LongTerm
        self.Reduction1 = Reduction1
        self.Reduction2 = Reduction2
        self.combinations = combinations
        self.GalaDinner = GalaDinner
        self.activity = activity
        self.sbi = sbi
        
        self.start_date = start_date if start_date is not None else self.contract_sheet.loc[0,"first date"]
        self.end_date = end_date if end_date is not None else self.contract_sheet.loc[len(contract_sheet)-1,"second date"]

        self.contract_dictionary = {
                    "eb1": EarlyBooking1,
                    "eb2": EarlyBooking2,
                    "lt": LongTerm,
                    "senior": Senior,
                    "reduc1": Reduction1,
                    "reduc2": Reduction2,
                    "combinations": combinations,
                    "gd": GalaDinner,
                    "activity": activity,
                    "sbi": sbi
                }    

