from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv("VERTEX_PROJECT_ID"))
print(os.getenv("VERTEX_ENDPOINT_ID"))