from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', 
                         time_slots=['09:00', '09:15'],
                         morning_slots=['09:00', '09:15'],
                         afternoon_slots=['14:00', '14:15'],
                         dates=[{'date': '2025-10-22'}],
                         version='3.5',
                         csrf_token='')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
