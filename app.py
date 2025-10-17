from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
from flask_socketio import SocketIO, emit
import argparse
import os
from functools import wraps
from flask import request, Response

USERNAME = 'admin'
PASSWORD = 'secret'

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Access denied.\n', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__)
socketio = SocketIO(app)

# Set the upload folder to the 'upload' directory next to the script
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory shared text (not stored permanently)
shared_text = ""

@requires_auth
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@requires_auth
@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" href="/favicon.ico">
        <title>File Upload and Real-time Text Sharing</title>
        <style>
            body {
                background-color: #0d0d0d;
                color: #d4e157;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background-color: #1b1b1b;
                padding: 20px;
                border-radius: 10px;
                width: 50%;
                box-shadow: 0px 0px 20px 0px #d4e157;
            }
            h1 {
                margin-bottom: 20px;
            }
            form {
                margin-bottom: 20px;
            }
            input[type=file], input[type=text] {
                margin: 10px 0;
                color: #d4e157;
                background-color: #2e2e2e;
                border: 1px solid #d4e157;
                padding: 10px;
                border-radius: 5px;
                width: 100%;
            }
            input[type=submit], button {
                color: #d4e157;
                background-color: #2e2e2e;
                border: 1px solid #d4e157;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }
            input[type=submit]:hover, button:hover {
                background-color: #d4e157;
                color: #0d0d0d;
            }
            progress {
                width: 100%;
                height: 20px;
                border-radius: 5px;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 5px 0;
            }
            a {
                color: #d4e157;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload Files & Share Text</h1>
            
            <!-- File upload form -->
            <form id="uploadForm" method=post enctype=multipart/form-data action="/upload">
                <input type="file" name="file" multiple><br>
                <input type="submit" value="Upload">
            </form>
            <progress id="progressBar" value="0" max="100" style="display: none;"></progress>
            <div id="status"></div>

            <!-- Shared real-time text box -->
            <h2>Shared Text Box</h2>
            <input type="text" id="sharedTextBox" autocomplete="off" placeholder="Type something..." />
            
            <h2>Files Available for Download</h2>
            <ul>
            {% for file in files %}
                <li><a href="/files/{{file}}">{{file}}</a></li>
            {% endfor %}
            </ul>
        </div>

        <!-- Include socket.io -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.min.js"></script>
        <script type="text/javascript">
            const socket = io();

            // File upload handler
            const form = document.getElementById('uploadForm');
            const progressBar = document.getElementById('progressBar');
            const status = document.getElementById('status');

            form.onsubmit = function(event) {
                event.preventDefault();
                const formData = new FormData(form);

                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/upload', true);

                xhr.upload.onprogress = function(event) {
                    if (event.lengthComputable) {
                        progressBar.style.display = 'block';
                        const percentComplete = (event.loaded / event.total) * 100;
                        progressBar.value = percentComplete;
                        status.innerHTML = `Upload Progress: ${percentComplete.toFixed(2)}%`;
                    }
                };

                xhr.onload = function() {
                    if (xhr.status === 200) {
                        status.innerHTML = 'Upload complete!';
                        window.location.reload();
                    } else {
                        status.innerHTML = 'Upload failed!';
                    }
                };

                xhr.send(formData);
            };

            // Real-time text sharing handler
            const sharedTextBox = document.getElementById('sharedTextBox');

            // Listen for user input and send it to the server
            sharedTextBox.addEventListener('input', function() {
                const text = sharedTextBox.value;
                socket.emit('update_text', text);
            });

            // Listen for text updates from the server
            socket.on('update_text', function(data) {
                sharedTextBox.value = data;
            });

            // When connected, request the current shared text
            socket.on('connect', function() {
                socket.emit('request_initial_text');
            });
            
            // Add connection status indicator
            socket.on('connect', function() {
                console.log('Connected to server');
            });
            
            socket.on('disconnect', function() {
                console.log('Disconnected from server');
            });
        </script>
    </body>
    </html>
    ''', files=files)


@app.route('/upload', methods=['POST'])
@requires_auth
def upload_file():
    files = request.files.getlist('file')
    for file in files:
        if file.filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect(url_for('index'))

@app.route('/files/<filename>')
@requires_auth
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Handle WebSocket connection for real-time text updates
@socketio.on('request_initial_text')
def handle_request_initial_text():
    global shared_text
    emit('update_text', shared_text)

@socketio.on('update_text')
def handle_update_text(text):
    global shared_text
    shared_text = text
    emit('update_text', shared_text, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='5000', debug=True)
