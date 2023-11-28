from fastapi import APIRouter, Response
from api.db import db

from typing import List

from api.models.feed import FeedModel


router = APIRouter(prefix="/feeds")


@router.get("/tiempoReal", response_description="Obtener feeds con tiempo real", response_model=List[FeedModel], response_model_exclude_none=True)
async def get_feeds_tr(response: Response):
  try:
    feeds = await db.find("feeds", {"tiempoReal": {"$exists": True}}, projection={"idFeed": 1, "tiempoReal": 1})
  except:
    response.status_code = 500
    return []
  else:
    if len(feeds) == 0:
      response.status_code = 204
    return feeds