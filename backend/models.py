"""Pydantic schemas shared by API endpoints."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

Mode = Literal["walk", "bike", "car", "tram", "bus", "metro", "train"]


class Point(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class RouteRequest(BaseModel):
    origin: Point
    destination: Point
    mode: Mode = "walk"


class Place(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=160)
    name_en: str = Field(min_length=1, max_length=160)
    category: Literal["tourism", "business"]
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    visit_minutes: int = Field(ge=5, le=240)
    source: str = "osm"


class SmartRequest(BaseModel):
    city: str
    country: str = ""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    minutes: int = Field(ge=30, le=1440)
    mode: Mode = "walk"
    interest: Literal["all", "tourism", "business"] = "all"
    places: list[Place] = Field(default_factory=list, max_length=100)
    language: Literal["pl", "en"] = "pl"
    use_ai: bool = False


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    country: str = Field(default="", max_length=120)
    mode: Mode
    minutes: int = Field(ge=30, le=1440)
    stops: list[dict] = Field(default_factory=list, max_length=20)
    itinerary: str = Field(default="", max_length=6000)


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    mode: Mode | None = None
    minutes: int | None = Field(default=None, ge=30, le=1440)
