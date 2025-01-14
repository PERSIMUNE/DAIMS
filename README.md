# DfMD
Datasheets for Medical Datasets app.

Requirements for Data and Data Dictionary files:
- .csv or .xlsx files
- no value are case sensitive
- List of NaN values:
  -   ["#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "N/A", "NA", "NULL", "NaN", "None", "n/a", "nan", "null", "na", "-"]

Data Dictionary:
- Requiered Columns:
  - "variable type"
    - only values permitted:
      -"continuous", "categorical", "date and time" 
  - "role"
    - only values permitted:
      - "outcome", "feature", "identifier", "other"
      - variables labeled as "other" are not evaluated in the app.
      - If multiple variables are labeled as "identifier" only first is checked
      
Data:
  - List of allowed characters:
    -   '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
  
