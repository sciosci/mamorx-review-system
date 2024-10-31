import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from fastapi import FastAPI
from app.api.endpoints import info, review
from app.config import settings

app = FastAPI()

app.include_router(info.router)
app.include_router(review.router, prefix="/review")