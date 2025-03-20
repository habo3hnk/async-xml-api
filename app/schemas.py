from pydantic import BaseModel, Field, ConfigDict
from typing import List


class TagCountResponse(BaseModel):
    count: int = Field(..., ge=0)

    model_config = ConfigDict(json_schema_extra={"example": {"count": 5}})


class TagAttributesResponse(BaseModel):
    attributes: List[str] = Field(...)

    model_config = ConfigDict(
        json_schema_extra={"example": {"attributes": ["attr1", "attr2", "attr3"]}}
    )
