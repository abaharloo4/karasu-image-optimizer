import os
import time
import shutil
import threading
from flask import Flask, request
from flask_cors import CORS
from backend.config import Config
from backend.api.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app()
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.after_request
    def add_header(response):
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response
        
    return app

def start_cleanup_thread():
    """Starts a daemon thread to clean up uploaded and processed files older than 24 hours"""
    def cleanup_loop():
        while True:
            try:
                current_time = time.time()
                for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER]:
                    if not folder.exists():
                        continue
                    for item in folder.iterdir():
                        if item.is_dir():
                            mtime = item.stat().st_mtime
                            # Check if the folder was modified more than 24 hours ago
                            if (current_time - mtime) > 24 * 3600:
                                shutil.rmtree(item)
                                print(f"Cleaned up expired directory: {item}")
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
            time.sleep(3600)  # Run every hour
            
    thread = threading.Thread(target=cleanup_loop)
    thread.daemon = True
    thread.start()

app = create_app()

if __name__ == '__main__':
    start_cleanup_thread()
    # Run the server on host 0.0.0.0 to make it accessible inside docker
    app.run(host='0.0.0.0', port=5001, debug=True)

