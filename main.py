from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import mission_route, feedback_route, data_analysis_route
import openai
import os


openai.api_key = os.getenv('OPENAI_API_KEY')
print(os.environ)
api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# Missions
api.include_router(mission_route.router)
api.include_router(feedback_route.router)
api.include_router(data_analysis_route.router)


if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)