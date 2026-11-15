"""TravelMate REST API. Start: uvicorn backend.main:app --reload"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from backend import db
from backend.models import PlanCreate, PlanUpdate, RouteRequest, SmartRequest
from backend.services.geo import search_cities, find_places, resolve_location
from backend.services.travel import estimate, transport
from backend.services.planner import build
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.initialize()
    yield


app = FastAPI(title="TravelMate API", version="1.0.0", lifespan=lifespan,
              description="Python trip planner (educational MVP)")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://127.0.0.1:7860,http://localhost:7860").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "TravelMate"}


@app.get("/api/cities/search")
def cities(q: str = Query(min_length=2, max_length=100), country: str = Query(default="", max_length=100)):
    return {"items": search_cities(q, country)}


@app.get("/api/places")
def places(city: str = Query(min_length=2, max_length=100), country: str = "",
           lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    items, source = find_places(city, country, lat, lon)
    return {"items": items, "source": source}


@app.get("/api/locations/resolve")
def location_resolve(q: str = Query(min_length=2, max_length=160),
                     city: str = Query(min_length=2, max_length=100),
                     country: str = Query(default="", max_length=100),
                     lat: float = Query(ge=-90, le=90),
                     lon: float = Query(ge=-180, le=180)):
    point = resolve_location(q, city, country, lat, lon)
    if point is None:
        raise HTTPException(404, "Location not found near selected city")
    return point


@app.get("/api/transport")
def local_transport(city: str = Query(min_length=2, max_length=100), country: str = "", mode: str = "walk"):
    if mode not in {"walk", "bike", "car", "tram", "bus", "metro", "train"}:
        raise HTTPException(422, "Unsupported transport mode")
    return {"items": transport(city, country, mode)}


@app.post("/api/routes/estimate")
def route_estimate(request: RouteRequest):
    return estimate(request.origin, request.destination, request.mode, external=True)


@app.post("/api/itineraries/suggest")
def suggest(request: SmartRequest):
    return build(request)


@app.get("/api/plans")
def plans():
    return {"items": db.list_plans()}


@app.post("/api/plans", status_code=201)
def create(data: PlanCreate):
    return db.create_plan(data)


@app.get("/api/plans/{plan_id}")
def get(plan_id: int):
    item = db.get_plan(plan_id)
    if not item:
        raise HTTPException(404, "Plan not found")
    return item


@app.put("/api/plans/{plan_id}")
def update(plan_id: int, data: PlanUpdate):
    item = db.update_plan(plan_id, data)
    if not item:
        raise HTTPException(404, "Plan not found")
    return item


@app.delete("/api/plans/{plan_id}", status_code=204)
def delete(plan_id: int):
    if not db.delete_plan(plan_id):
        raise HTTPException(404, "Plan not found")
