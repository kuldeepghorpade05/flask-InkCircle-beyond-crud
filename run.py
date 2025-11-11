import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Flask InkCircle API...")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    app.run(debug=True, host='0.0.0.0', port=8000)