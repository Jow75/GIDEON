import socket
import uvicorn

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def find_available_port(start_port: int = 8100, max_port: int = 8200) -> int:
    for port in range(start_port, max_port + 1):
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

if __name__ == "__main__":
    try:
        # Start looking from 8100 specifically to avoid 8000
        port = find_available_port(start_port=8100)
        print(f"\n" + "="*50)
        print(f"Gideon Core starting on dynamically assigned port: {port}")
        print("="*50 + "\n")

        # Run the API
        uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Failed to start server: {e}")
