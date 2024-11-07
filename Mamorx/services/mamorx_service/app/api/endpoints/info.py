from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return "MAMORX Service is running and accessible"