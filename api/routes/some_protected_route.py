from fastapi import APIRouter, Depends
from api.helper.auth_bearer import verify_token

router = APIRouter()

@router.get("/protected-route")
async def protected_endpoint(token_data: dict = Depends(verify_token)):
    # token_data contains the decoded JWT payload
    return {"message": "This is a protected route", "user": token_data} 