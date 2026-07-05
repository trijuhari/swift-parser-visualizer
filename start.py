import subprocess
import sys
import time
import signal

processes = []

def cleanup(sig, frame):
    print("\n🛑 Stopping SWIFT Reporting Tool...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    print("👋 All processes stopped.")
    sys.exit(0)

def main():
    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("🚀 Starting SWIFT Reporting Tool...")

    try:
        # 1. Start Backend API
        print("📦 Starting Flask Backend API on port 8766...")
        backend = subprocess.Popen(
            [sys.executable, "backend/app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(backend)

        # Give backend a moment to initialize
        time.sleep(1)

        # 2. Start Frontend server
        print("💻 Starting Python HTTP Web Server on port 8765...")
        frontend = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8765"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(frontend)

        print("\n🌐 SWIFT Reporting Tool is running successfully!")
        print("👉 Open http://localhost:8765 in your browser")
        print("💡 Press Ctrl+C at any time to stop both servers safely.\n")

        # Keep running
        while True:
            # Check if any process has exited unexpectedly
            if backend.poll() is not None:
                print("⚠️ Backend exited unexpectedly.")
                break
            if frontend.poll() is not None:
                print("⚠️ Frontend server exited unexpectedly.")
                break
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Error starting processes: {e}")
    finally:
        cleanup(None, None)

if __name__ == "__main__":
    main()
