# -*- coding: utf-8 -*-
"""
Written by Anne Svane Frahm, annesfrahm@gmail.com, CHIP Persimune, 2025.
"""

import streamlit as st
import pandas as pd
import numpy as np
import string
import io

#for downloading excel sheet
buffer = io.BytesIO()

#place holders for data and data dictionary(dd) uploads
data = None
dd = None

nan_values =  ["#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "N/A", "NA", "NULL", "NaN", "None", "n/a", "nan", "null", "na", "-"]

#flags checking if import has been succesfull
flag_data = 0
flag_dd = 0

#output excel sheet
sheet_out = pd.DataFrame(columns = ["#", "Mark if true", "Automatically checked", "Item", "Notification"])
sheet_out.set_index("#", inplace = True)

def man_check(n, txt):
    #function for setting up each manual check in the app
    #input:
    #n = (int) check number
    #text = (str) check text
    #Output:
    #sheet_row = (np.array) Line formatted for output dataframe

    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = txt
    st.write(f"{n}) {sheet_row[2]}")

    col1, col2 = st.columns(2)
    with col1:
        check = st.radio(label = "Mark if true", options = ["Pass", "Fail", "Unknown"], index = 2, key = "radio"+str(n))
    with col2:
        comment = st.text_area(label = "Comment (if not done):", key = "text"+str(n))

    #add row to output sheet
    sheet_row[0] = check
    sheet_row[1] = "No"
    sheet_row[3] = comment
    return(sheet_row)


#start of app interface

col1, mid, col2 = st.columns([5,1,10])
with col1:
    st.image('DAIMSlogo.svg', width=200)
with col2:
    st.title("DAIMS - Datasheets for AI and Medical Datasets") 

url_paper = "https://github.com/PERSIMUNE/DAIMS/blob/main/DAIMS_DatasetName_DDMMYYYY.md"
st.write("For instructions of use please view [Datasheets for AI and medical datasets (DAIMS)](%s)" % url_paper) #change when published!

citation = "To reference this tool, please cite:\n"\
+ "@article{marandi2025daims,\n" \
+ "\t title={Datasheets for AI and medical datasets (DAIMS): a data validation and documentation framework before machine learning analysis in medical research}, \n" \
+ "\t author={Ramtin Zargari Marandi and Anne Svane Frahm and Maja Milojevic}, \n" \
+ "\t journal={arXiv preprint arXiv:2501.14094}0,\n" \
+ "\t year={2025}, \n" \
+ "\t url={https://arxiv.org/abs/2501.14094} \n" \
+ "}\n"

st.text(citation)

#upload widgets for data and dd
st.subheader("Upload your Data file:")
csv_file = st.file_uploader("Choose a .csv or .xlsx data file")
st.subheader("Upload your Data Dictionary file:")
dict_file = st.file_uploader("Choose a .csv or .xlsx data dictionary file")

#import data file
if csv_file is not None:
    #check file format and import accordingly
    if csv_file.name.split(".")[-1].lower() == "csv":
        data = pd.read_csv(csv_file, keep_default_na= False, na_values = nan_values, dtype=str)
        st.subheader("Here's the data:")
        st.write(data)
        flag_data = 1
    elif csv_file.name.split(".")[-1].lower() == "xlsx":
        data = pd.read_excel(csv_file, keep_default_na= False, na_values = nan_values, dtype=str)
        st.subheader("Here's the data:")
        st.write(data)
        flag_data = 1
    else:
        st.subheader("Data file format not recognised")
        flag_data = 0

#import data dictionary file and check that it follows conditions
if dict_file is not None:
    #check file format and import accordingly
    if dict_file.name.split(".")[-1].lower() == "csv":
        dd = pd.read_csv(dict_file)
        st.subheader("Here's the data dictionary:")
        st.write(dd)
        flag_dd = 2
    elif dict_file.name.split(".")[-1].lower() == "xlsx":
        dd = pd.read_excel(dict_file)
        st.subheader("Here's the data dictionary:")
        st.write(dd)
        flag_dd = 2
    else:
        st.subheader("Data dictionary file format not recognised")
        flag_dd = 0

    #check if all required columns are in dd
    if flag_dd == 2:
        #lower case everything in dd
        ##column names
        dd.columns = map(str.lower, dd.columns)
        ##all non numeral data
        dd = dd.map(lambda s: s.lower() if type(s) == str else s)
        #check obligatory role column
        if "role" in dd.columns:
            #get values not matching permitted values
            wrong_role = dd.role[~dd.role.isin(["outcome", "feature", "identifier", "other"])]
            if len(wrong_role) > 0:
                flag_dd = 0
                st.write(f':red[Only values "outcome", "feature", "identifier" and "other" are permitted in Data Dictionary Role column. Not for instance: {wrong_role.iloc[0]}]')
        else:
            flag_dd = 0
            st.write(':red[Required column "Role" is not in Data Dictionary]')
        #check obligatory "varible type" column
        if "variable type" in dd.columns:
            #get values not matching permitted values
            wrong_var_type = dd["variable type"][~dd["variable type"].isin(["continuous", "categorical", "date and time"])]
            if len(wrong_var_type) > 0:
                flag_dd = 0
                st.write(f':red[Only values "continuous", "categorical" and "date and time" are permitted in Data Dictionary Variable Type column. Not for instance: {wrong_var_type.iloc[0]}]')
        else:
            flag_dd = 0
            st.write(':red[Required column "Variable Type" is not in Data Dictionary]')
        #check obligatory "varible name" column
        if "variable name" not in dd.columns:
            st.write(':red[Required column "Variable Name" is not in Data Dictionary]')
        
        if flag_dd == 2:
            flag_dd = 1

#go through data checks
st.subheader("Performing tests:")
if flag_data == 1 and flag_dd == 1:
    
    #lower case everything in data
    data = data.map(lambda s: s.lower().strip() if type(s) == str else s)
    data.rename(columns = lambda s : s.lower().strip() if type(s) == str else s, inplace = True)

    #remove variables with role "other"
    others = dd[dd.role == "other"]["variable name"]
    data_full = data.copy()
    for i in others:
        if i in data.columns:
            data = data.drop(i, axis = 1)
    
    #get list of categorical variables
    cat_rows =  dd[dd["variable type"] == "categorical"]
    cat_cols = cat_rows["variable name"]

    #find column lable as ID
    id_row =  dd[dd.role == "identifier"]
    id_col = id_row["variable name"]

     #remove ID(s) from list
    if len(id_col) > 0 :
        #cat_cols = cat_cols.drop(id_col, errors='ignore')
        cat_cols = cat_cols[~cat_cols.isin(id_col)]

    #remove columns not in data (and features with Role "other") from list
    cat_cols = cat_cols[cat_cols.isin(data.columns)]

    #find continuous variables
    cont_n = dd["variable name"][dd["variable type"]== "continuous"]
    cont_n = cont_n[cont_n.isin(data.columns)]
    conts = data[cont_n]

    #check if range column is in dd
    if "categories or range" in dd.columns:
        flag_range = 1
    else:
        flag_range = 0

    #convert variables marked as continous to float
    data_float = conts.apply(pd.to_numeric, errors ="coerce")
    data_float_comb = data_float.copy()

    cat_data = data[cat_cols]
    for i in cat_cols:
        data_float_comb[i] = pd.factorize(data[i])[0]
        data_float_comb[i] = data_float_comb[i].replace(-1, np.nan)

    #region 1 Wide format: Each row is an instance, and each column is a variable (in addition to patient ID and target/outcome variable) 
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Wide format: Each row is an instance, and each column is a variable (in addition to patient ID and target/outcome variable)"
    #check if all data columns is datadict rows
    var_not_in_dd = data.columns[~data.columns.isin(dd["variable name"])]
    #rows in data not in dd - check failed
    if len(var_not_in_dd) > 0 :
        st.write(f"1) {sheet_row[2]}: :red[NO]")
        error = f"There are columns not described in the Data Dictionary. For instance: {var_not_in_dd[0]}"
        st.write(f":red[{error}]")
        sheet_row[3] = error
        sheet_row[0] = "Fail"
    #check passed
    else:
      st.write(f"1) {sheet_row[2]}: :green[Yes]")
      sheet_row[0] = "Pass"
    #add row to output sheet
    sheet_row[1] = "Yes"
    sheet_out.loc[1] = sheet_row
    #endregion
   
    #region 2 Each patient has a unique identifier (ID)
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Each patient has a unique identifier (ID)"

    #no ID - check failed
    if len(id_row) == 0:
        st.write(f"2) {sheet_row[2]}: :red[NO]")
        error = "No column has Role as Identifier in Data Dictionary."
        st.write(f":red[{error}]")
        sheet_row[3] = error
        sheet_row[0] = "Fail"
    #ID found
    else:
        #(first)ID is in data
        if id_col.iloc[0] in data.columns:
            ids = data[id_col.iloc[0]]
            #all values are unique - check passed 
            if ids.is_unique:
                st.write(f"2) {sheet_row[2]}: :green[Yes]")
                sheet_row[0] = "Pass"
                error = ""
            #duplicate IDs present -check failed
            else:
                id_dubs = ids[ids.duplicated()]
                st.write(f"2) {sheet_row[2]}: :red[NO]")
                sheet_row[0] = "Fail"
                error = f"Some IDs are duplicated. For instance: {str(id_dubs.values[0])}"
                st.write(f":red[{error}]" )
        #(first) ID not present - check failed
        else:
            st.write(f"2) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"The column with Role as Identifier {id_col.iloc[0]} is not in Data."
            st.write(f":red[{error}]")
    
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[2] = sheet_row
    #endregion

    #region 3 No Unicode character
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "No Unicode character"
    #costum defined char list?
    #char_allowed = string.ascii_lowercase + string.digits
    #function for checking for non-standard character
    def check_cha(x):
        y = False
        for i in str(x):
            if i not in string.printable:
                y = True
        return y

    #check columns
    col_wrong = data.columns[data.columns.map(lambda x : check_cha(x))]
    #check elements in data
    data_wrong = data[data.map(lambda x : check_cha(x))]
    data_wrong.dropna(axis = 0, how="all", inplace= True)
    data_wrong.dropna(axis = 1, how="all", inplace= True)
    #wrong char in col - failed
    if len(col_wrong) > 0:
        st.write(f"3) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = f"There are columns with non-standard characters in data. For instance: {col_wrong[0]}."
        st.write(f":red[{error}]")
    #wrong char in values - failed
    elif len(data_wrong) > 0:
        st.write(f"3) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        wrong_example = data_wrong.notna().idxmax()
        error = f"There are values with non-standard characters in data. For instance: {data_wrong[wrong_example.index[0]].loc[wrong_example.iloc[0]]}."
        st.write(f":red[{error}]")
    #all in allowed chars - passed
    else:
        st.write(f"3) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""

    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[3] = sheet_row

    #endregion

    #region 4 No duplicate rows and columns 
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "No duplicate rows and columns"

    #check if columns are duplicated
    #dub_col = data.columns[data.columns.duplicated()]
    dub_row = data[data.duplicated()]
    #duplicated rows - check failed
    if len(dub_row) > 0 :
        st.write(f"4) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = f"There are duplicated rows in data. For instance: {dub_row.iloc[0]}."
        st.write(f":red[{error}]")
    #no duplicates found
    else:
        st.write(f"4) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""    

    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[4] = sheet_row

    #endregion

    #region 5 Test if first column is patient ID
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "First column is patient ID"
    #more than one ID - check failed
    if len(id_row) > 1:
        st.write(f"5) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = "Multiple columns have Role as Identifiers"
        st.write(f":red[{error}]")
    #no ID - check failed
    elif len(id_row) == 0:
        st.write(f"5) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = "No column has Role as Identifier in Data Dictionary"
        st.write(f":red[{error}]")
    #exactly one ID
    elif len(id_row) == 1:
        #ID first column in Data - check passed 
        if data_full.columns[0] == id_col[0]:
            st.write(f"5) {sheet_row[2]}: :green[Yes]")
            error = ""
            sheet_row[0] = "Pass"
        #ID not first column - check failed
        else:
            st.write(f"5) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"Column with Role as Identifier is: {id_col[0]}. First column is: {data_full.columns[0]}."
            st.write(f":red[{error}]")
    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[5] = sheet_row
    #endregion

    #region 6 Last column is the outcome variable or the main outcome in the case of multiple outcomes 
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Last column is the outcome variable or the main outcome in the case of multiple outcomes"
    #more than one ID - check failed
    outcome_row =  dd[dd.role == "outcome"]
    outcome_col = outcome_row["variable name"].values
    #no outcome - check failed
    if len(id_row) == 0:
        st.write(f"6) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = "No column has Role as outcome in Data Dictionary"
        st.write(f":red[{error}]")
    #check if outcome is last
    else:
        #(one of) outcome last column in Data - check passed 
        if data_full.columns[-1] in outcome_col:
            st.write(f"6) {sheet_row[2]}: :green[Yes]")
            error = ""
            sheet_row[0] = "Pass"
        #outcome not last column - check failed
        else:
            st.write(f"6) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"Column(s) with Role as Outcome is: {outcome_col}. Last column is: {data_full.columns[-1]}."
            st.write(f":red[{error}]")
    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[6] = sheet_row
    #endregion

    #region 7 (8) (13) No further separator (e.g., “,” for numbers with four digits or longer such as 1,050,099) and no extra characters “()”,”[]”, “<>”, “//”, “||” and ”{}”. The only acceptable separator is the decimal point. 
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "No further separator (e.g., “,” for numbers with four digits or longer such as 1,050,099) and no extra characters “()”,”[]”, “<>”, “//”, “||” and ”\{\}”. The only acceptable separator is the decimal point"

    #list of allowed characters 
    allowed_cha = list(map(str, np.arange(10)))+list([".", "-"])
    #set up check functions
    def cont_checkcha(x):
        # returns true if all cha allowed
        return(all(c in allowed_cha for c in x))
    
    def countdot(x):
        # returns True if more than one .
        y = x.split(".")
        if len(y) > 2:
            return True
        else: 
            return False
    
    def check_minus(x):
        #returns True if misplaced minus
        if "-" in x:
            x = x[1:]
            if len(x) > 0:
                 if "-" in x:
                     return True
                 else: 
                     return False
            else:
             return True
        else:
            return False
             
    
    flag_cont = 0

    for col in conts.columns:
        #remove NaN
        conts_col_not_nan = conts[col][~conts[col].isna()]
        #get bad values
        x = conts[col][~conts[col].apply(cont_checkcha)]
        z = conts[col][conts[col].apply(check_minus)]
        y = conts[col][conts[col].apply(countdot)]

        if (len(x) > 0) and flag_cont == 0:
            flag_cont = 1
            bad_col = col
            bad_val = x.iloc[0]
            error = f"There are non permitted characters in a continuous variable. For instance: {bad_val} In column: {bad_col}"
        elif (len(y) > 0) and flag_cont == 0:
            flag_cont = 1
            bad_col = col
            bad_val = y.iloc[0]
            error = f"There are multiple \".\"s in a continuous variable. For instance: {bad_val} In column: {bad_col}."
        elif (len(z) > 0) and flag_cont == 0:
            flag_cont = 1
            bad_col = col
            bad_val = z.iloc[0]
            error = f"There are misplaced \"-\"s in a continuous variable. For instance: {bad_val} In column: {bad_col}."

    if flag_cont == 1:
        st.write(f"7) {sheet_row[2]}: :red[NO]")
        st.write(f":red[{error}]")
        sheet_row[0] = "Fail"
    else:
        st.write(f"7) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""
        if len(conts.columns) == 0:
                    st.write(":grey[NB: No columns marked as \"continuous\" found]")
            
    #add row to output sheet
    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[7] = sheet_row
    #endregion

    #region 8 (7) All missing entries are indicated by the same entry (such as NA for not available)  ### TEXT IS WRONG AND SHOULD BE UPDATED
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "All missing entries are indicated by the same entry (e.g., either \"missing\" or an empty field for not available) "
    #NaN present in data - check failed
    if data.isnull().values.any():
        st.write(f"8) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        idx, idy = np.where(pd.isnull(data))
        error = f"There are NaN values in data. For instance column: {data.columns[idy[0]]} row: {data.index[idx[0]]} in data."
        st.write(f":red[{error}]")
    #"na" present in data - check failed
    elif (data == "na" ).any().any():
        st.write(f"8) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        idx, idy = np.where(data == "na")
        error = f"There are \"na\" values in data. For instance column: {data.columns[idy[0]]} row: {data.index[idx[0]]} in data."
        st.write(f":red[{error}]")
    #"-" present in data - check failed
    elif (data == "-" ).any().any():
        st.write(f"8) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        idx, idy = np.where(data == "-")
        error = f"There are \"-\" values in data. For instance column: {data.columns[idy[0]]} row: {data.index[idx[0]]} in data."
        st.write(f":red[{error}]")
    #both empty fields and "missing" present in data - check failed
    elif (data == "" ).any().any() and (data == "missing").any().any():
        st.write(f"8) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        idx, idy = np.where(data == "")
        jdx, jdy = np.where(data == "missing")
        error = f"There are \"missing\" and empty values in data. For instance column: {data.columns[idy[0]]} row: {data.index[idx[0]]}, and column: {data.columns[jdy[0]]} row: {data.index[jdx[0]]} in data."
        st.write(f":red[{error}]")
    #no errors found - check passed 
    else :
        st.write(f"8) {sheet_row[2]}: :green[Yes]")
        error = ""
        sheet_row[0] = "Pass"
    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[8] = sheet_row
    #endregion

    #region 9 (10) (20) No instance has all-missing variables 

    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "No instance has all-missing variables"

    all_miss = data.columns[data.isna().all(0)]

    if len(all_miss) == 0:
        st.write(f"9) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""
    else:
        st.write(f"9) {sheet_row[2]}: :red[NO]")
        error = f"Some columns has all missing values. For instance column: {all_miss[0]}."
        st.write(f":red[{error}]")
        sheet_row[0] = "Fail"

    #add row to output sheet
    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[9] = sheet_row
    #endregion

    #region 10 (15) (10) A data dictionary (codebook) is provided that defines all variables, their types (categorical, ordinal, and interval) and units (e.g. kg) 
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "A data dictionary (codebook) is provided that defines all variables, their types (continuous, categorical or date and time) and units (e.g., kg)"

    #columns in data not in dd - check failed
    if len(var_not_in_dd) > 0 :
        st.write(f"10) {sheet_row[2]}: :red[NO]")
        error = f"There are columns not described in the Data Dictionary. For instance: {var_not_in_dd[0]}"
        st.write(f":red[{error}]")
        sheet_row[0] = "Fail"
    #variable type not defined for all data columns - check failed  
    elif "units" not in dd.columns:
        st.write(f"10) {sheet_row[2]}: :red[NO]")
        error = "No column named \"units\" in Data Dictionary."
        st.write(f":red[{error}]")
        sheet_row[0] = "Fail"
    #There are missing values in units column - check failed
    elif dd.units.isna().values.any():
        example = dd["variable name"][dd.units.isna()].values[0]
        st.write(f"10) {sheet_row[2]}: :red[NO]")
        error = f"There are missing values in the \"units\" column in the Data Dictionary. For instance for: {example}."
        st.write(f":red[{error}]")
        sheet_row[0] = "Fail"
    else:
        st.write(f"10) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""

    #add row to output sheet
    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[10] = sheet_row
    #endregion

    #region 11 (12) (22) The actual data values for continuous variables are within the range listed in data dictionary (Check consistency between data dictionary and actual data values) 
    
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "The actual data values for continuous variables are within the range listed in data dictionary"

    cont_flag = 0
    cont_comment = 0

    if flag_range == 1:
        for i in data_float.columns:
            if cont_flag == 0:
                range_values = dd[dd["variable name"] == i]["categories or range"].iloc[0].split(";")

                if len(range_values) != 2:
                    cont_flag = 2
                else:
                    try: [r_1, r_2] = [float(range_values[0]), float(range_values[1])]
                    except: cont_flag = 2

                if cont_flag == 2:
                    error = f"Range is not listed correctly in Data Dictionary with two numerical values separeted by a \";\". For instance for variable: {i}."
                elif data_float[i].dropna().between(r_1,r_2).all() == False:
                    cont_flag = 1
                    bad_cont = i
                    bad_cont_val = data_float[i].dropna()[~data_float[i].dropna().between(r_1,r_2)].iloc[0]
                elif len(data_float[i].dropna()) == 0:
                    cont_comment = 1
                    bad_cont = i

    if flag_range == 0:
            st.write(f"11) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"There are no column called \"Categories or range\" in the Data Dictionary"
            st.write(f":red[{error}]") 

    elif cont_flag == 0:
            st.write(f"11) {sheet_row[2]}: :green[Yes]")
            sheet_row[0] = "Pass"
            error = ""
            if len(cont_n) == 0:
                st.write(":grey[NB: No variables marked as \"continous\" found]")
            elif cont_comment == 1:
                st.write(f":grey[NB: Variable {bad_cont} has no numerical values.]")

    else:
        st.write(f"11) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = "There are values outside of the range defined in the Data Dictionary"
        st.write(f":red[{error}]") 

    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[11] = sheet_row

    #endregion

    #region 12 (9) (17) Categorical variables have all their categories listed in the data dictionary  (All the entries for each variable follow the same format (units for numerical variables and categories for categorical variables) 
    #set up line for output sheet)
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Categorical variables have all their categories listed in the data dictionary"
   
    cat_flag = 0

    if flag_range == 1:
        for i in cat_cols:
            #get potential catogirical values from dd
            cat_values = dd[dd["variable name"] == i]["categories or range"].iloc[0].split(";")
            #remove white space
            cat_values = [cat_val.strip() for cat_val in cat_values]

            #check all values are in potential values
            if cat_flag == 0 and not set(data[i].unique()).issubset(cat_values):
                cat_flag = 1
                bad_cat = i
                bad_cat_val = list(set(data[i].unique()) - set(cat_values))[0]

    #no range column - check failed
    if flag_range == 0:
            st.write(f"12) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"There are no column called \"Categories or range\" in the Data Dictionary"
            st.write(f":red[{error}]") 
    #no values not listed found - check passed
    elif cat_flag == 0:
            st.write(f"12) {sheet_row[2]}: :green[Yes]")
            sheet_row[0] = "Pass"
            error = ""
            if len(cat_cols) == 0:
                st.write(":grey[NB: No non-ID columns marked as \"categorical\" found]")
    #categories not listed found - check failed
    else:
        st.write(f"12) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = f"There are rare categories in the data not listed in the Data Dictionary. For instance: [{bad_cat_val}] in column: {bad_cat}."
        st.write(f":red[{error}]")       

    #add row to output sheet
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[12] = sheet_row
    #endregion

    #region 13 (14) (9) Rare categories in categorical variables are grouped 
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Rare categories in categorical variables are grouped"

    flag_c = 1
    for i in cat_cols:
        freq = data[i].value_counts(normalize=True, ascending=True)
        freq_rare = freq[freq < 0.05]
        if len(freq_rare > 0):
            flag_c = 0
            rare_col = i
            rare_1 = freq_rare.index[0]
            #rare_2 = freq_rare.index[1]
    #No rare categories found - check passed 
    if flag_c == 1:
                st.write(f"13) {sheet_row[2]}: :green[Yes]")
                sheet_row[0] = "Pass"
                error = ""
                if len(cat_cols) == 0:
                    st.write(":grey[NB: No non-ID columns marked as \"categorical\" found]")
    else:
            st.write(f"13) {sheet_row[2]}: :red[NO]")
            sheet_row[0] = "Fail"
            error = f"There are rare categories in data. For instance: [{rare_1}] in column: {rare_col}."
            st.write(f":red[{error}]")
    
    sheet_row[3] = error
    sheet_row[1] = "Yes"
    sheet_out.loc[13] = sheet_row
    #endregion

    #region 14 (11) (21) Perfectly collinear variables are removed 

    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Perfectly collinear variables are removed"

    #get correlation matrix
    corr_matrix = data_float_comb.corr()

    #zero values in diagonal
    np.fill_diagonal(corr_matrix.values, 0)

    #find correlated values
    perf_corr = corr_matrix[corr_matrix > 0.999]

    perf_corr = perf_corr.dropna(how = 'all', axis = 0)
    perf_corr = perf_corr.dropna(how = 'all', axis = 1)
    
    #check passed 
    if len(perf_corr) == 0:
        st.write(f"14) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""
    #check failed
    else:
        st.write(f"14) {sheet_row[2]}: :red[NO]")
        error = f"Some columns are perfectly collinear. For instance variables: {perf_corr.columns[0]} and {perf_corr.notna().idxmax()[perf_corr.columns[0]]}]"
        st.write(f":red[{error}")
        sheet_row[0] = "Fail"

    #add row to output sheet
    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[14] = sheet_row
    #endregion

    #region 15 (13) (24) Irrelevant observations that could skew the results or cause bias (e.g., outliers or extreme values that do not reflect normal conditions) are removed 
    
    #set up line for output sheet
    sheet_row = np.full(4, "", dtype= 'object')
    sheet_row[2] = "Irrelevant observations that could skew the results or cause bias (e.g., outliers or extreme values that do not reflect normal conditions) are removed"

    out_flag = 0
    cont_comment = 0

    for i in data_float.columns:
        if out_flag == 0:
            #check if not all NaN
            if len(data_float[i].dropna()) > 0:
                #get interquantile range
                q1 = data_float[i].quantile(.25)
                q3 = data_float[i].quantile(.75)
                iqr = q3 - q1

                #find outliers
                outliers = data_float[i].dropna()[~data_float[i].dropna().between((q1-3*iqr),(q3+3*iqr))]

                if len(outliers) > 0:
                    out_flag = 1
                    cont_out = i
                    cont_out_val = outliers.iloc[0]
            #if all NaN
            elif cont_comment == 0:
                cont_out = i
                cont_comment = 1

    #no outliers found - check passed                 
    if out_flag == 0:
        st.write(f"15) {sheet_row[2]}: :green[Yes]")
        sheet_row[0] = "Pass"
        error = ""
        if len(cont_n) == 0:
            st.write(":grey[NB: No variables marked as \"continous\" found]")
        elif cont_comment == 1:
            st.write(f":grey[NB: Variable {cont_out} has no numerical values.]")

    else:
        st.write(f"15) {sheet_row[2]}: :red[NO]")
        sheet_row[0] = "Fail"
        error = f"There are outliers in the data. For instance variable: {cont_out} has value: {cont_out_val}."
        st.write(f":red[{error}]")    
              
    sheet_row[1] = "Yes"
    sheet_row[3] = error
    sheet_out.loc[15] = sheet_row
    #endregion

    #region Manual checks
    st.subheader("Manual checks:")
    #16 (15) Date and time are formatted as described in the data dictionary (for example 05-11-2022 12:23 DD-MM-YYYY CET) 
    sheet_out.loc[16] = man_check(16, "Date and time are formatted as described in the data dictionary (for example 05-11-2022 12:23 DD-MM-YYYY CET)")
    #17 (18) (12) Numerical entries have “.” as decimal separator (i.e. 1.2 not 1,2) 
    sheet_out.loc[17] = man_check(17, "Numerical entries have “.” as decimal separator (i.e. 1.2 not 1,2)")
    #18 (19) (14) Non-English entries are translated to English. Non-Latin scripts are transformed to Latin scripts. 
    sheet_out.loc[18] = man_check(18, "Non-English entries are translated to English. Non-Latin scripts are transformed to Latin scripts")
    #19 (22) (19) The terms used in the dataset follow international standards
    sheet_out.loc[19] = man_check(19, "The terms used in the dataset follow international standards")
    #20 (21) (18) All entries for each variable follow the same standard (e.g. older entries may have different standards or definitions) 
    sheet_out.loc[20] = man_check(20, "All entries for each variable follow the same standard (e.g. older entries may have different standards or definitions)")
    #21 (17) (11) Erroneous data (out of range or meaningless) are removed or corrected (e.g., a BMI value of 2000)
    sheet_out.loc[21] = man_check(21, "Erroneous data are corrected or removed (e.g., a BMI value of 2000)")
    #22 (23) (8) Informative missingness is properly encoded (e.g. “not tested” when it was deemed unnecessary to test) 
    sheet_out.loc[22] = man_check(22, "Informative missingness is properly encoded (e.g. “not tested” when it was deemed unnecessary to test") 
    #23 (20) (16) Variable irrelevant for study are removed  (i.e. non-generalizable variables that could not relate to the outcome, e.g., billing ID or personal contact information) 
    sheet_out.loc[23] = man_check(23, "Variable irrelevant for study are removed  (i.e. non-generalizable variables that could not relate to the outcome, e.g., billing ID or personal contact information)") 
    #24 (25) sensitive data
    sheet_out.loc[24] = man_check(24, "No sensitive data including name, address, or identity number of the participants (patients) are included ")

    #endregion
else:
    st.write("Upload data and data dictionary to begin.")

#scoring
st.subheader("Checklist Scoring")
if flag_data == 1 and flag_dd == 1:
    score_butt = st.button("Calculate score")
    if score_butt:
        score = (sheet_out["Mark if true"] == "Pass").sum()
        score_per = round(score*100/len(sheet_out), 2)
        st.write(f"Your Completeness Score is {score}/{len(sheet_out)} or {score_per}%")
else:
    st.write("Upload data and data dictionary to begin.")

#download check sheet
st.subheader("Download Checklist (.xlsx)")
if flag_data == 1 and flag_dd == 1:
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
   
        sheet_out.to_excel(writer)
        writer.close()
        output_name = "check_list_" + ".".join(csv_file.name.split(".")[:-1]) + ".xlsx"
        #download_button = st.button("Download")
        #if download_button:
        #    sheet_out.to_excel(output_name)
        
        st.download_button(
            label="Download",
            data=buffer,
            file_name=output_name,
            mime="application/vnd.ms-excel"
        )
            
else:
    st.write("Upload data and data dictionary to begin.")
