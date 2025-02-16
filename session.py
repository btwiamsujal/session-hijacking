from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import time
import uuid
from datetime import datetime, timedelta

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Change if using MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["session_tracker"]
sessions_collection = db["sessions"]

# ChromeDriver Path
CHROME_DRIVER_PATH = "chromedriver.exe"  # Change if needed

# Get Browser Session ID using Selenium
def get_browser_session_id():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Specify your path to ChromeDriver
    service = Service(CHROME_DRIVER_PATH)
    
    # Launch Chrome with the configured options
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open Instagram or any website that requires a session
    driver.get("https://www.instagram.com")

    # Wait for the page to load and cookies to be set
    time.sleep(5)

    # Extract cookies from the browser
    cookies = driver.get_cookies()

    # Close the browser
    driver.quit()

    # Iterate through the cookies and get the session ID
    for cookie in cookies:
        if cookie["name"] == "sessionid":
            return cookie["value"]  # Return the session ID

    return None  # If session ID not found

# Class for Managing MongoDB Sessions
class MongoDBSessionManager:
    def __init__(self, user_id):
        self.user_id = user_id

    def create_session(self, duration_minutes):
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": self.user_id,
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat(),
            "blocked": False,
            "emergency_used": False,
            "active": True
        }

        sessions_collection.insert_one(session_data)
        return session_id

    def validate_session(self, session_id):
        session = sessions_collection.find_one({"session_id": session_id, "user_id": self.user_id})
        if not session:
            print("Session not found in database.")
            return False

        print(f"Session found: {session}")

        end_time = datetime.fromisoformat(session["end_time"])

        if datetime.now() > end_time and not session["blocked"]:
            print("Session expired. Blocking now.")
            sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": {"blocked": True, "active": False}}
            )
            return False

        return True

    def emergency_access(self, session_id):
        session = sessions_collection.find_one({"session_id": session_id, "user_id": self.user_id})
        
        if session and session["blocked"] and not session["emergency_used"]:
            sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "end_time": (datetime.now() + timedelta(minutes=5)).isoformat(),
                        "blocked": False,
                        "emergency_used": True,
                        "active": True
                    }
                }
            )
            return True
        return False

# Main Function
def main():
    user_id = input("Enter your unique user ID: ")
    session_manager = MongoDBSessionManager(user_id)

    try:
        session_id = input("Enter session ID (press enter for new session): ")
        if session_id:
            if not session_manager.validate_session(session_id):
                print("Invalid or expired session!")
                return
        else:
            limit = int(input("Enter daily time limit (minutes): "))
            session_id = session_manager.create_session(limit)
            print(f"New session created. ID: {session_id} (Save this for emergency access!)")

        browser_session_id = get_browser_session_id()
        if browser_session_id:
            print(f"Browser Session ID: {browser_session_id}")
        else:
            print("Could not retrieve browser session ID.")

        start_time = datetime.now()

        while True:
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSession paused. Updating database...")
        sessions_collection.update_one({"session_id": session_id}, {"$set": {"active": False}})

if __name__ == "__main__":
    main()
