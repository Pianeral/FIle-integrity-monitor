# app.py - Flask Web Dashboard + Real-Time File Integrity Monitoring (with Folder Selection)
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Shared list for recent events
recent_events = []
monitoring_active = False
observer = None
watch_directory = "monitored_folder"  # Default folder - can be changed via dashboard

class IntegrityHandler(FileSystemEventHandler):
    def __init__(self, watch_path):
        self.watch_path = Path(watch_path).resolve()

    def _get_rel_path(self, path):
        try:
            return str(Path(path).resolve().relative_to(self.watch_path))
        except:
            return str(path)

    def _send_alert(self, event_type, path):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rel_path = self._get_rel_path(path)
        message = f"[{timestamp}] {event_type.upper()} → {rel_path}"
        
        recent_events.append(message)
        if len(recent_events) > 50:
            recent_events.pop(0)
        
        # Send live update to browsers
        socketio.emit('new_alert', {'message': message, 'type': event_type.lower()})

    def on_created(self, event):
        if not event.is_directory:
            self._send_alert('NEW FILE', event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._send_alert('MODIFIED', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._send_alert('DELETED', event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._send_alert('MOVED', f"{event.src_path} → {event.dest_path}")

def start_monitoring():
    global observer, monitoring_active
    if monitoring_active:
        return
    print(f"[INFO] Starting monitoring on: {watch_directory}")
    event_handler = IntegrityHandler(watch_directory)
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    observer.start()
    monitoring_active = True
    socketio.emit('status_update', {'status': 'Active'})

def stop_monitoring():
    global observer, monitoring_active
    if observer:
        print("[INFO] Stopping monitoring")
        observer.stop()
        observer.join()
    monitoring_active = False
    socketio.emit('status_update', {'status': 'Stopped'})

@app.route('/')
def dashboard():
    return render_template('dashboard.html', events=recent_events, current_folder=watch_directory)

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('status_update', {'status': 'Active' if monitoring_active else 'Stopped'})
    emit('current_folder', {'path': watch_directory})

@socketio.on('set_folder')
def handle_set_folder(data):
    global watch_directory
    new_path = data['path'].strip()
    
    if os.path.isdir(new_path):
        watch_directory = new_path
        print(f"[INFO] Folder changed to: {new_path}")
        emit('response', {'data': f'Folder updated to: {new_path}'})
        emit('current_folder', {'path': new_path})
        
        # Auto-restart monitoring if active
        if monitoring_active:
            stop_monitoring()
            start_monitoring()
    else:
        emit('response', {'data': f'Error: Invalid folder path - {new_path}'})

@socketio.on('start_monitoring')
def handle_start():
    start_monitoring()
    emit('response', {'data': 'Monitoring started!'})

@socketio.on('stop_monitoring')
def handle_stop():
    stop_monitoring()
    emit('response', {'data': 'Monitoring stopped!'})

if __name__ == '__main__':
    print("Launching Flask + SocketIO server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)