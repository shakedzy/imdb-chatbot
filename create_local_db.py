import csv 
import sys
import toml
import sqlite3 

# Enable large fields in input files
csv.field_size_limit(sys.maxsize)

def flatten_list(nested_list):
    flattened = []

    def flatten(sublist):
        for item in sublist:
            if isinstance(item, list):
                flatten(item)
            else:
                flattened.append(item)

    flatten(nested_list)
    return flattened


print("Starting...")
conn = sqlite3.connect('imdb.db')
cursor = conn.cursor()

for table, fields in toml.load("tables.toml").items():
    print(f"Creating table: {table}...")

    # Reading table names from tables.toml and creating each table
    sql = f"CREATE TABLE {table} ("
    for field in fields.keys():
        match field.split(' ')[1].lower():
            case "(int)":
                field_type = "INTEGER"
            case "(float)":
                field_type = "REAL"
            case _:
                field_type = "TEXT"
        sql += f"{field.split(' ')[0]} {field_type}, "
    sql = sql[:-2] + ")"  # removes the last comma and space added from the line above
    cursor.execute(sql)
    
    # Read the data from the TSV files and add it to the tables
    # This is done line-by-line due to the size of the files
    with open(f'data/{table.replace("_",".")}.tsv', 'r') as file:
        tsv_reader = csv.reader(file, delimiter='\t')

        header = next(tsv_reader) 
        num_columns = len(header)

        for row in tsv_reader:
            
            # handling parsing issues, some tabs are over-looked due to misplaced quotes
            if len(row) < num_columns:
                row = [v.split('\t') for v in row]
                row = flatten_list(row)
            
            row = [v if v != '\\N' else None for v in row]
            
            try:
                cursor.execute(f'INSERT INTO {table} VALUES ({",".join(["?"] * num_columns)})', row)
            except Exception as e:
                print(f'Exception {e}:', table, row)

conn.commit()
conn.close()

print('Done.')
