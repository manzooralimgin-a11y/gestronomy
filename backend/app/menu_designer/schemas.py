from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MenuTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    layout_type: str
    template_config_json: dict | None
    is_system: bool
    created_at: datetime


class MenuTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    layout_type: str = "single_page"
    template_config_json: dict | None = None


class MenuDesignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    template_id: int | None
    design_data_json: dict | None
    translations_json: dict | None
    status: str
    language: str
    created_at: datetime
    updated_at: datetime | None


class MenuDesignCreate(BaseModel):
    name: str
    template_id: int | None = None
    design_data_json: dict | None = None
    language: str = "de"


class MenuDesignUpdate(BaseModel):
    name: str | None = None
    template_id: int | None = None
    design_data_json: dict | None = None
    translations_json: dict | None = None
    language: str | None = None


class PublishResponse(BaseModel):
    id: int
    status: str
    message: str
