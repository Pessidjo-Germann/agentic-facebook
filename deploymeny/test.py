from vertexai import agent_engines

adk_app = agent_engines.get('projects/313916322392/locations/us-central1/reasoningEngines/2089925313797554176')
#session = adk_app.create_session(user_id="helloo",state={"user_id": "10", "name": "germann"})
#print(f"Session created with ID: {session}")
#adk_app.list_sessions(user_id="germanno")
# 3073122355250200576  1920200850643353600
#session = adk_app.get_session(user_id="germanno", session_id="3073122355250200576")
#print(f"Session retrieved with ID: {session}")
for event in adk_app.stream_query(
    user_id="hello",
    session_id='1197531440124788736',  # Optional
    message= {'parts': [{'text': "genere l'images"}], 'role': 'user'}
):
  print(event)
