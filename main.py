import threading
from io_system import start_io_system
from camera_control import app, start_camera_control  # Updated import to reflect new function name

def main():
    """
    Main entry point of the program.
    Launches the touchscreen interface for the user to select options.
    """
    print("Initializing system...")
    result = start_io_system()  # Starts the touchscreen interface to display options
    
    # Start Flask server in a separate thread to be available for streaming
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080, threaded=True))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait for the selection result to determine next steps
    if result == 'Chest Pass':
        print("Chest Pass selected, starting camera control phase...")
        start_camera_control()  # Updated to call the new `start_camera_control` function

    elif result == 'Reset':
        print("Resetting system...")
        # You could add any specific reset logic here if needed

if __name__ == "__main__":
    main()
