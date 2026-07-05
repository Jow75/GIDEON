import os
import sys
from core.consciousness import SystemConsciousness

def main():
    print("\n--- Gideon Initialization ---")

    # Check for API Key
    if not os.environ.get("NVIDIA_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

    if not os.environ.get("NVIDIA_API_KEY"):
        print("Error: NVIDIA_API_KEY environment variable is not set.")
        print("Please export it or add it to a .env file.")
        sys.exit(1)

    try:
        gideon = SystemConsciousness()
        print("System Consciousness: Online")
        print("World State: Connected")
        print("Gideon is ready. Type 'quit' to quit.\n")
    except Exception as e:
        print(f"Failed to initialize Gideon: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Gideon: Shutting down. Goodbye.")
                break

            if not user_input.strip():
                continue

            response = gideon.process_input(user_input)
            print(f"\nGideon: {response}\n")

        except KeyboardInterrupt:
            print("\nGideon: Shutting down via interrupt. Goodbye.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()
