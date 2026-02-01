# File Integrity Monitoring Tool

Real-time file change detection with web dashboard.

## Features
- Monitors any folder
- Real-time alerts (create/modify/delete/move)
- Flask + SocketIO web UI

## Setup
pip install -r requirements.txt
python app.py
 
 ## Running the Dashboard

1. Make sure you’re in the project folder:
   ```bash
   cd path/to/FILE_INTEGRITY_MONITOR
2. Start the server:
   flask run --host=0.0.0.0 --port=5000
3. Open the dashboard:
   On the same computer: http://127.0.0.1:5000 or http://localhost:5000
4. In the dashboard:
   - Enter the full folder path (e.g. C:\Users\YourName\Documents\MyFiles)
   - Click Set Folder
   - Click Start Monitoring
   - Make changes in the folder → watch live alerts appear instantly
