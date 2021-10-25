# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd

# ClASSES

# Input file class
# Read dataset and validate it
class InputFile:
    def __init__(self, inputfile="Daimler-test-data.json"):
       self.inputfile = inputfile   
    
    def read_file(self):
        # Read json file
        df_read = pd.read_json(self.inputfile)
        return df_read
    
    def validate_dataset(self, df_transposed): 
        # Check null values
        check_null_values = df_transposed.isnull().values.any()
        
        if check_null_values:
            raise Exception("Null values found in the dataset")
        else:
            # Verify all values have prefix att-a...j- aka column+"-"
            for column in df_transposed:
                # Check that all values in column have prefix column+"-"
                df_without_prefix = df_transposed[column].apply(lambda x: x[:6]==(column+"-"))
                # At this point we have an array with True/False unique values
                df_without_prefix_unique = df_without_prefix.unique()
                # If any value is false we raise an exception
                if(len(df_without_prefix_unique)>1 or ~df_without_prefix_unique[0]):
                    raise Exception("Values without '"+column+"-' string found in the dataset column "+column)
                
                # Check that all values in column have numeric suffix
                df_int_values = df_transposed[column].apply(lambda x: x[6:].isnumeric())
                # At this point we have an array with True/False unique values
                df_int_values_unique = df_int_values.unique()
                # If any value is false we raise an exception
                if(len(df_int_values_unique)>1 or ~df_int_values_unique[0]):
                    raise Exception("Values without numeric suffix found in the dataset column "+column)
                    
                    
# Requested number class
# Request sku code to the user and validate that exists and format
class RequestedNumber:
    def __init__(self):
        # Request sku code
        self.inserted_sku =  input ("Hi, please enter sku code (sku-number): ")
    
    def validate_sku(self, df_read):
        # Validate 'sku-' prefix and that is in the dataframe
        if self.inserted_sku[:4]!="sku-":
            raise Exception("please enter an sku code with 'sku-' prefix (sku-number)")
        elif not (self.inserted_sku in df_read.columns):
            raise Exception("sku code not found in dataset, please enter an sku code (sku-number)")


# Recommendation class
# Score 
class Recommendation:
    def __init__(self, inserted_sku):
        self.index_sku = int(inserted_sku[4:])-1
        
    def get_recommendations(self, df_transposed, len=10):
        self.origin_sku = df_transposed.iloc[[self.index_sku]]
        self.len=len
        columns = df_transposed.columns
        df_transposed['score_tmp']=0
        df_transposed['score']=0

        for column in columns:
            target_value = df_transposed.iloc[self.index_sku][column]
            df_transposed['score_tmp'] = df_transposed[column].apply(lambda x: 1 if x==target_value else 0)
            df_transposed['score']=df_transposed['score']+df_transposed['score_tmp']
        
        self.df_scored = df_transposed.sort_values(by='score', ascending=False).drop(['score_tmp'], axis=1).head(self.len+1)

    def print_recommendations(self):
        print("Solution before formating:")
        print(self.df_scored, "\n")
        pd.set_option("display.max_rows", None, "display.max_columns", None)

        df_final = self.df_scored.drop('score', axis=1)

        for i in df_final.index:
            print(df_final.loc[[i]].to_json(orient="index"))
        
        print("\n")

# FUNCTIONS        
# Main function
def main():
    try:
        # Begin dataset read process
        print_log("[Info] Starting", "read")
        
        # Create file object and read json dataset
        inputFileObject = InputFile(inputfile)
        df_read = inputFileObject.read_file()
   
        # End dataset read process
        print_log("[Info] Ending", "read")
           
        # Begin dataset validation process
        print_log("[Info] Starting", "validation")

        # Transpose and validate dataset
        df_transposed = df_read.T
        inputFileObject.validate_dataset(df_transposed)
        
        # End dataset validation process
        print_log("[Info] Ending", "validation")
        
        # Begin user request and validation process
        print_log("[Info] Starting", "user request")
        
        # Request user sku code and validate it
        requestedSkuObject = RequestedNumber()
        requestedSkuObject.validate_sku(df_read)
        
        # End user request and validation process
        print_log("[Info] Ending", "user request")
        
        # Begin get recommendation process
        print_log("[Info] Starting", "get recommendations")
    
        # Score similar sku codes and return 10 with higher score in descending
        # order
        recommendationObject = Recommendation(requestedSkuObject.inserted_sku)
        recommendationObject.get_recommendations(df_transposed)
        recommendationObject.print_recommendations()
        
        # End get recommendation process
        print_log("[Info] Ending", "get recomendations")
    
    except Exception as e:
        print("[Error] "+str(e)) 
    
    

# This function return current time
def calculate_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# This function prints log
def print_log(prefix, process):
    print(prefix+" "+process+" process at", calculate_time())

    
if __name__ == "__main__":
    inputfile="Daimler-test-data.json"

    print_log("[Info] Starting", "main")
    
    main()
    
    print_log("[Info] Ending", "main")
