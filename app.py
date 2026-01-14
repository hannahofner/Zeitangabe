from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import db
import wienerlinien
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_only'  # Insecure, for demo only

# Initialize DB on startup
if not os.path.exists(db.DB_NAME):
    db.init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if db.create_user(username, password):
        return redirect(url_for('index')) # Redirect to login/index
    else:
        return "Username already exists", 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = db.get_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials", 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

import stops_data

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'], stops=stops_data.STOPS)

@app.route('/api/departures')
def api_departures():
    stop_id = request.args.get('stop_id')
    if not stop_id:
        return jsonify([])
    data = wienerlinien.get_departures(stop_id)
    return jsonify(data)

@app.route('/api/favourites', methods=['GET', 'POST', 'DELETE'])
def api_favourites():
    if 'user_id' not in session:
        return "Unauthorized", 401
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        favs = db.get_favourites(user_id)
        return jsonify(favs)
    
    if request.method == 'POST':
        data = request.json
        stop_id = data.get('stop_id')
        stop_name = data.get('stop_name')
        if db.add_favourite(user_id, stop_id, stop_name):
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "exists"}), 400

    return "Method not allowed", 405

@app.route('/api/favourites/<int:fav_id>', methods=['DELETE'])
def delete_favourite(fav_id):
    if 'user_id' not in session:
        return "Unauthorized", 401
    db.remove_favourite(fav_id, session['user_id'])
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
