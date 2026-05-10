#Basic E-Commerce Platform(Quantum Cart)

A dynamic, lightweight e-commerce storefront built with Python, Flask, and MS SQL Server. 

## 🚀 Features
* **Automated Data Pipeline:** Utilizes Python `requests` to consume the DummyJSON API and seed the MS SQL database with a 100-item inventory.
* **Dynamic Storefront:** Renders randomized product grids using SQL `NEWID()` for an optimized, fresh user experience.
* **Asynchronous Cart System:** Implements AJAX for seamless, page-reload-free cart updates.
* **Secure Authentication:** Features user registration, login, and protected dashboard routes with hashed passwords via `werkzeug.security`.

## 💻 Tech Stack
* **Frontend:** HTML5, Bootstrap CSS, JavaScript (AJAX)
* **Backend:** Python 3, Flask Web Framework
* **Database:** MS SQL Server (`pyodbc`)

## 🛠️ How to Run Locally
1. Clone this repository.
2. Run the `schema.sql` script in MS SQL Server to generate the tables.
3. Update the `SERVER` name in `app.py` and `seed.py` to match your MS SQL instance.
4. Run `python seed.py` to populate the database.
5. Run `python app.py` to start the server at `http://127.0.0.1:5000`.
