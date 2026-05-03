from fastapi import APIRouter

from ..data.app_data import DATA_SOURCES
from ..db import query

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/flavors")
def get_flavors():
    return query.fetch_flavors()


@router.get("/routes")
def get_routes():
    return query.fetch_routes()


@router.get("/chapters")
def get_chapters():
    return query.fetch_chapters()


@router.get("/data-sources")
def get_data_sources():
    return DATA_SOURCES


@router.get("/search")
def search(q: str = ""):
    return query.search(q)
