from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to my Development Journal API!"

@app.route('/api/entries')
def get_entries():
    """Return sample journal entries"""
    entries = [
        {
            "id": 1,
            "title": "Started learning Flask",
            "content": "Today I created my first Flask API!",
            "date": "2026-03-06"
        },
        {
            "id": 2,
            "title": "Git practice",
            "content": "Learning Git and GitHub workflows",
            "date": "2026-03-06"
        }
    ]
    return jsonify(entries)

@app.route('/api/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)