import os
import sys

import vertexai
from dotenv import load_dotenv
from vertexai.preview import reasoning_engines

from multi_tool_agent.agent import root_agent


def main():
    # Load environment variables
    load_dotenv()
    project_id = "facebook-agent-461716"
    location = "us-central1"
    staging_bucket = "gs://run-sources-facebook-agent-461716-us-central1"

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        sys.exit(1)
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        sys.exit(1)

    # Initialize Vertex AI
    print(f"Initializing Vertex AI with project={project_id}, location={location}")
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket,
    )

    # Create the app
    print("Creating local app instance...")
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Create a session
    print("Creating session...")
    session = app.create_session(user_id="testo_user")
    print("Session created:")
    print(f"  Session ID: {session.id}")
    print(f"  User ID: {session.user_id}")
    print(f"  App name: {session.app_name}")

    # List sessions
    print("\nListing sessions...")
    sessions = app.list_sessions(user_id="testo_user")
    if hasattr(sessions, "sessions"):
        print(f"Found sessions: {sessions.sessions}")
    elif hasattr(sessions, "session_ids"):
        print(f"Found session IDs: {sessions.session_ids}")
    else:
        print(f"Sessions response: {sessions}")

    # Send a test query
    print("\nReady to chat! Type 'quit' to exit.")
    while True:
        test_message = input("You: ")
        if test_message.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        print(f"\nSending message: {test_message}")
        print("Response:")
        for event in app.stream_query(
            user_id="testo_user",
            session_id=session.id,
            message=test_message,
        ):
            print(event)
        print("\n" + "-"*50)


if __name__ == "__main__":
    main()
