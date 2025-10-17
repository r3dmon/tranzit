

# FileShare & Real-time Text Collaboration

A Flask-based web application that combines file sharing capabilities with real-time text collaboration. This application allows authenticated users to upload files, download them, and share text in real-time across multiple connected clients.

## Features

- **File Upload & Download**: Upload multiple files with progress tracking and download them later
- **Real-time Text Collaboration**: Share and edit text in real-time across multiple connected clients
- **Authentication**: Secure access with basic HTTP authentication
- **Responsive Dark UI**: Modern dark-themed interface with responsive design
- **WebSocket Communication**: Real-time updates using Socket.IO

## Requirements

- Python 3.6+
- Flask
- Flask-SocketIO
- A modern web browser with JavaScript enabled

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fileshare-realtime.git
cd fileshare-realtime
```

2. Install the required packages:
```bash
pip install flask flask-socketio

or

 conda config --add channels conda-forge
 conda install flash_socketio flask
```

3. Create an upload directory:
```bash
mkdir upload
```

## Usage

1. Run the application:
```bash
python app.py --
```

2. Open your web browser and navigate to `http://localhost:5000`

3. When prompted, enter the default credentials:
   - Username: `admin`
   - Password: `secret`

4. Use the interface to:
   - Upload files (single or multiple)
   - Download previously uploaded files
   - Share and edit text in real-time with other connected users

## Configuration

### Authentication

To change the default credentials, modify these lines in `app.py`:

```python
USERNAME = 'admin'  # Change this to your desired username
PASSWORD = 'secret'  # Change this to your desired password
```

### Server Configuration

To change the host and port, modify the last line in `app.py`:

```python
socketio.run(app, host='0.0.0.0', port='5000', debug=True)
```

- `host`: Set to `'0.0.0.0'` to make the server accessible from other devices on the network
- `port`: Change the port number if needed
- `debug`: Set to `False` in production

## Project Structure

```
fileshare-realtime/
├── app.py              # Main application file
├── upload/             # Directory for uploaded files
├── static/             # Static files (favicon)
└── README.md           # This file
```

## Security Considerations

- This application uses basic HTTP authentication, which sends credentials in plain text. Consider using HTTPS in production.
- The default credentials should be changed before deploying to a production environment.
- File uploads are not validated for content type. Consider adding validation if security is a concern.
- The shared text is stored in memory and will be lost when the server restarts.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

- **File uploads not working**: Ensure the `upload` directory exists and has write permissions.
- **Real-time text not updating**: Check that JavaScript is enabled in your browser and that there are no firewall restrictions blocking WebSocket connections.
- **Authentication issues**: Verify that you're using the correct credentials as defined in the `app.py` file.

## Future Enhancements

- User authentication system with multiple users
- File type validation and size limits
- Persistent storage for shared text
- File organization into folders
- File preview functionality
- Mobile app companion