import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import time

app = Flask(__name__)

# MySQL config – must match docker-compose
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'mysql')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'flaskuser')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'flaskpass')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'flaskdb')

mysql = MySQL(app)

def init_db():
    retry = 5
    while retry > 0:
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                )
            """)
            mysql.connection.commit()
            cur.close()
            print("Database initialized")
            return
        except Exception as e:
            print("Waiting for MySQL...", e)
            retry -= 1
            time.sleep(5)

@app.before_first_request
def startup():
    init_db()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', (new_message,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
