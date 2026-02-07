import os
from dotenv import load_dotenv

# Try loading .env
print("Loading .env...")
loaded = load_dotenv()
print(f"load_dotenv() returned: {loaded}")

# Check key
key = os.getenv("OPENWEATHER_API_KEY")
if key:
    print(f"SUCCESS: Found OPENWEATHER_API_KEY (Length: {len(key)})")
    print(f"First 4 chars: {key[:4]}...")
else:
    print("FAILURE: OPENWEATHER_API_KEY not found in environment.")

# Check CWD
print(f"Current Working Directory: {os.getcwd()}")
print("Files in CWD:", os.listdir())
