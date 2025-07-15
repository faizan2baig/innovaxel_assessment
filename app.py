from flask import Flask, request, jsonify, redirect
import mysql.connector
import random, string
from config import DB_CONFIG

app = Flask(__name__)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    short_code = generate_short_code()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (%s, %s)", (original_url, short_code))
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'short_url': request.host_url + short_code})

@app.route('/<short_code>')
def redirect_url(short_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return jsonify({'error': 'Short URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
