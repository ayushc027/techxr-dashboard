from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pymysql
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        db='your_db',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect('/')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    tables, columns, data = [], [], []
    selected_table = None

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[f'Tables_in_{conn.db.decode()}'] for row in cursor.fetchall()]

        if request.method == 'POST':
            selected_table = request.form.get('table')
            cursor.execute(f"DESCRIBE {selected_table}")
            columns = cursor.fetchall()
            cursor.execute(f"SELECT * FROM {selected_table} LIMIT 100")
            data = cursor.fetchall()
    conn.close()

    return render_template('index.html', tables=tables, columns=columns, data=data, selected_table=selected_table)

@app.route('/export/<string:table>/<string:filetype>')
def export(table, filetype):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows)
    output = BytesIO()

    if filetype == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', download_name=f'{table}.csv', as_attachment=True)
    elif filetype == 'excel':
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=f'{table}.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[f'Tables_in_{conn.db.decode()}'] for row in cursor.fetchall()]

    total_tables = len(tables)
    table_stats = []
    total_rows = 0

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        row_count = cursor.fetchone()['count']
        table_stats.append({'name': table, 'rows': row_count})
        total_rows += row_count

    conn.close()
    return render_template('dashboard.html', total_tables=total_tables, total_rows=total_rows, table_stats=table_stats)
