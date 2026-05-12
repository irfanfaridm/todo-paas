from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return jsonify({
        "aplikasi": "To-do List API",
        "status": "aktif",
        "versi": "1.0.0"
    })


@app.route("/health")
def health():
    return jsonify({"status": "sehat"})


@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos ORDER BY id ASC;")
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(todos)


@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"error": "Title wajib diisi"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (title) VALUES (%s) RETURNING *;",
        (title,)
    )
    todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(todo), 201


@app.route("/todos/<int:id>", methods=["PUT"])
def update_todo(id):
    data = request.get_json()
    completed = data.get("completed")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE todos SET completed = %s WHERE id = %s RETURNING *;",
        (completed, id)
    )
    todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if todo is None:
        return jsonify({"error": "Todo tidak ditemukan"}), 404

    return jsonify(todo)


@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s RETURNING *;", (id,))
    todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if todo is None:
        return jsonify({"error": "Todo tidak ditemukan"}), 404

    return jsonify({"message": "Todo berhasil dihapus"})


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)