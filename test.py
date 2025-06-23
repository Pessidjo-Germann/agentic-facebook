from vertexai import agent_engines
#projects/232125896337/locations/us-central1/reasoningEngines/7714534220290326528
deployments = agent_engines.list()
if not deployments:
    print("No deployments found.")
print("Deployments:")
for deployment in deployments:
    print(f"- {deployment.resource_name}")
# agent_engine = agent_engines.get('9127538603377819648')
# agent_engine.list()
# remote_session = agent_engine.create_session(user_id="germann@gmail.com")
# print("Created session:")
# print(f"  Session ID: {remote_session['id']}")
# print(f"  User ID: {remote_session['user_id']}")
# print(f"  App name: {remote_session['app_name']}")


# for event in agent_engine.stream_query(
#         user_id="germann@gmail.com",
#         session_id="5931571112491089920",
#         message="tu connais le userid de l'utilisateur?",
       
#     ):
#         print(event)