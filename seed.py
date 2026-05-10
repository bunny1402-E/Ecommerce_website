import requests
import pyodbc
import sys



conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  
    'DATABASE=EcommerceDB;'          
    'Trusted_Connection=yes;'        
)
cursor = conn.cursor()

print("Fetching products from DummyJSON API...")
url = "https://dummyjson.com/products?limit=0"
response = requests.get(url)

print(f"API Server responded with status code: {response.status_code}")

if response.status_code != 200:
    print("\n[ERROR] The API is currently down.")
    sys.exit() 


data = response.json()
products_list = data.get('products', [])


print("Inserting data into MS SQL...")
print("Cleaning old data...")
cursor.execute("DELETE FROM Products") 

for item in products_list:
    price_inr = round(float(item['price']) * 83.0, 2)
   
    image_url = item.get('thumbnail', '')
    
    cursor.execute('''
        INSERT INTO Products (ProductID, Title, Price, Description, Category, ImageURL)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (item['id'], item['title'], price_inr, item['description'], item['category'], image_url))


conn.commit()
cursor.close()
conn.close()



print("Database successfully seeded with new products!")
