from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import FileService, TagService
from app.schemas import TagCountResponse, TagAttributesResponse

router = APIRouter()


@router.post("/api/file/read", response_model=bool)
async def read_file(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> bool:
    return await FileService(db).process_file(file)


@router.get("/api/tags/get-count", response_model=TagCountResponse)
async def get_tag_count(
    file_name: str, tag_name: str, db: AsyncSession = Depends(get_db)
) -> TagCountResponse:
    return await TagService(db).get_tag_count(file_name, tag_name)


@router.get("/api/tags/attributes/get", response_model=TagAttributesResponse)
async def get_tag_attributes(
    file_name: str, tag_name: str, db: AsyncSession = Depends(get_db)
) -> TagAttributesResponse:
    return await TagService(db).get_tag_attributes(file_name, tag_name)
