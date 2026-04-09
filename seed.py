import requests
import pyodbc
import sys

# 1. Connect to MS SQL Server
# REMEMBER: Change this to your actual server name!
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  
    'DATABASE=EcommerceDB;'          
    'Trusted_Connection=yes;'        
)
cursor = conn.cursor()

# 2. Fetch data from the DummyJSON API
print("Fetching products from DummyJSON API...")
url = "https://dummyjson.com/products?limit=100"
response = requests.get(url)

print(f"API Server responded with status code: {response.status_code}")

if response.status_code != 200:
    print("\n[ERROR] The API is currently down.")
    sys.exit() 

# DummyJSON puts the list of items inside a dictionary key called 'products'
data = response.json()
products_list = data['products']

# 3. Loop through products and insert into MS SQL
print("Inserting data into MS SQL...")
print("Cleaning old data...")
cursor.execute("DELETE FROM Products") 
# This clears the table so 'ID 1' can be inserted again without conflict.
for item in products_list:
    cursor.execute('''
        INSERT INTO Products (ProductID, Title, Price, Description, Category, ImageURL)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (item['id'], item['title'], item['price'], item['description'], item['category'], item['thumbnail']))

# 4. Save and Close
conn.commit()
cursor.close()
conn.close()



print("Database successfully seeded with products!")