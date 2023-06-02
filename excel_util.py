import pandas as pd
import json

def run_generator() -> str:
    path = input("Enter Excel File Path: ")

    table_name = input("Enter data table name: ")
    def_table = input("Enter table of definitions")

    skip_rows = input("Enter number of rows to skip for data")
    skip_rows_def = input("Enter number of rows to skip for defs")

    columns_column = input("Enter column of columns: ")
    defs_column = input("Enter column of definitions: ")

    start_date = input("Enter expected start date for file usage")
    end_date = input("Enter expected end date of file usage (enter 0 for null): ")

    return generate_config(path, table_name, def_table, skip_rows, 
                           skip_rows_def, columns_column, 
                           defs_column, start_date, end_date)

def generate_config (path, table_name, def_table, 
                     skip_rows, skip_rows_def, columns_column,
                     defs_column, start_date, end_date=None) -> str:

    filename = path.split('/')[-1]

    data = pd.read_excel(path, sheet_name=table_name, skiprows=skip_rows)
    defs = pd.read_excel(path, sheet_name=def_table, skiprows=skip_rows_def)

    columns = list(set(defs[columns_column].to_list()).intersection(data.columns.to_list()))

    defs_dict = defs.set_index(columns_column)[defs_column].to_dict()

    schema = []

    for c in columns:
        type = {"name": None, "type": None, "description": None}

        type["name"] = c

        for i in data[c]:
            if isinstance(i, (int, float, complex)):
                type["type"] = "NUMERIC"
            elif isinstance(i, str):
                type["type"] = "STRING"

        type["description"] = defs_dict[c]

        schema.append(type)

    load = {
        "createDisposition": "CREATE_IF_NEEDED",
        "destinationTableDescription": table_name,
        "fieldDelimiter": ",",
        "quoteCharacter": "",
        "sourceFormat": "CSV",
        "tableName": table_name,
        "writeDisposition": "WRITE_TRUNCATE",
        "skipRows": skip_rows,
        "schema": schema
    }

    config = {"filenamePattern": filename,
            "effectiveStartDate": start_date, 
            "effectiveEndDate": end_date,
            "action": "import",
            }
    
    config["load"] = load
    
    wrapper_list = [config]

    return json.dumps(wrapper_list, indent=4)
    

def convert_xlsx_csv(config_file, data_path, dest_path):
    config = json.loads(config_file)

    for c in config:
        data = pd.read_excel(data_path, sheet_name=c["load"], skiprows=c["load"]["skipRows"])
        data.to_csv(f'dest_path/{c["load"]["tableName"]}.csv')

