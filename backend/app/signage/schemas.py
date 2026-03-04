from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ── Screens ──
class SignageScreenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    location: str | None
    screen_code: str
    resolution: str
    orientation: str
    is_active: bool
    current_playlist_id: int | None
    last_ping_at: datetime | None
    created_at: datetime


class SignageScreenCreate(BaseModel):
    name: str
    location: str | None = None
    resolution: str = "1920x1080"
    orientation: str = "landscape"


class SignageScreenUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    resolution: str | None = None
    orientation: str | None = None
    is_active: bool | None = None
    current_playlist_id: int | None = None


# ── Content ──
class SignageContentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content_type: str
    content_data_json: dict | None
    duration_seconds: int
    is_active: bool
    created_at: datetime


class SignageContentCreate(BaseModel):
    title: str
    content_type: str
    content_data_json: dict | None = None
    duration_seconds: int = 15


class SignageContentUpdate(BaseModel):
    title: str | None = None
    content_type: str | None = None
    content_data_json: dict | None = None
    duration_seconds: int | None = None
    is_active: bool | None = None


# ── Playlists ──
class SignagePlaylistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    items_json: list | None
    schedule_json: dict | None
    is_active: bool
    created_at: datetime


class SignagePlaylistCreate(BaseModel):
    name: str
    items_json: list | None = None
    schedule_json: dict | None = None


class SignagePlaylistUpdate(BaseModel):
    name: str | None = None
    items_json: list | None = None
    schedule_json: dict | None = None
    is_active: bool | None = None
