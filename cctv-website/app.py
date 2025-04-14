from flask import Flask, render_template, request, redirect, session, url_for, flash
import pyodbc
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages
app.config["PERMANENT_SESSION_LIFE_TIME"] = timedelta(minutes = 2)
DATABASE_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=TSLL-ICT-494F\\SQLEXPRESS;"
    "DATABASE=user_table;"
    "Trusted_Connection=yes;"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    address = request.form['address']
    national_id = request.form['national_id']
    date_str = request.form['date']
    message = request.form['message']

    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    try:
        conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO [user_table].[dbo].[contact] (name, address, national_id, date, message) VALUES (?, ?, ?, ?, ?)",
            (name, address, national_id, date, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Contact submitted successfully.")
        return redirect(url_for('contact', success = 1))
    except Exception as e:
        
        print(f"An error occurred during submission: {e}")
        success = request.args.get('success', 0)
        return redirect(url_for('contact', success = success))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [user_table].[dbo].[admins] WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()  
            if user:
                
                print('Login successful!')
                return redirect(url_for('admin_contact'))
            
            else:
                print('Invalid credentials. Please try again.')
        except Exception as e:
            print(f"An error occurred during login: {e}")
    
    return render_template('login.html')



    
@app.route('/admin_contact')
def admin_contact():
    try:
        conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, address, national_id, date, message FROM [user_table].[dbo].[contact]")
        contacts = cursor.fetchall()
        print(contacts)  
    
        conn.close()
        return render_template('admin_contact.html', contacts = contacts)
    except Exception as e:
        print(f"Error: {e}") 
        return f"An error occurred while fetching the contact data: {e}"


@app.route('/delete_contact/<string:national_id>', methods=['POST'])
def delete_contact(national_id):
    try:
        conn = pyodbc.connect(DATABASE_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM [user_table].[dbo].[contact] WHERE national_id = ?", (national_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_contact'))
    except Exception as e:
        return f"An error occurred while deleting the contact: {e}"


if __name__ == '__main__':
    app.run(debug=True)
