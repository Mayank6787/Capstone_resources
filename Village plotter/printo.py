import pandas as pd

# Read the Excel file
excel_data = pd.read_excel('data.xlsx')

# Convert to JSON
json_data = excel_data.to_json('data.json', orient='records', indent=4)

print("Excel data has been converted to JSON!")
