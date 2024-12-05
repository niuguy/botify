from fastapi import APIRouter


router = APIRouter(tags=["chat"])


@router.post("/chat")
# TODO  return http response with status code 200
async def chat() -> None:
    pass
