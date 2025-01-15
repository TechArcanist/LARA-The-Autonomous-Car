from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection settings
DB_HOST = 'localhost'
DB_NAME = 'voice_query_vaman'
DB_USER = 'postgres'  # Replace with your PostgreSQL username
DB_PASSWORD = 'vaman'  # Replace with your PostgreSQL password

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route('/quer', methods=['GET'])
def query():
    question = request.args.get('question', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM quer WHERE question ILIKE %s", ('%' + question + '%',))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({'answer': result[0]})
    else:
        return jsonify({'error': 'Answer not found!'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
