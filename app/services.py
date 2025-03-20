from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
import xml.etree.ElementTree as ET
from app.models import FileModel, TagModel, AttributeModel
from app.schemas import TagCountResponse, TagAttributesResponse


class FileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _save_file(self, file_name: str) -> FileModel:
        result = await self.db.execute(
            select(FileModel).filter(FileModel.name == file_name)
        )
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Файл уже существует")

        new_file = FileModel(name=file_name)
        self.db.add(new_file)
        await self.db.commit()
        await self.db.refresh(new_file)
        return new_file

    async def _validate_file(self, file: UploadFile) -> None:
        if not file.filename or not file.filename.lower().endswith(".xml"):
            raise HTTPException(
                status_code=400, detail="Загруженный файл не является XML-файлом."
            )

    async def _parse_xml(self, content: bytes) -> ET.Element:
        try:
            return ET.fromstring(content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Недопустимый формат XML.")

    async def process_file(self, file: UploadFile) -> bool:
        await self._validate_file(file)

        content = await file.read()
        root = await self._parse_xml(content)

        if not file.filename:
            raise HTTPException(status_code=400, detail="Недопустимое имя файла")

        saved_file = await self._save_file(file.filename)

        processor = XMLProcessor(self.db, saved_file.id, saved_file.name)
        await processor.process_element(root)

        return True


class XMLProcessor:
    def __init__(self, db: AsyncSession, file_id: int, file_name: str):
        self.db = db
        self.file_id = file_id
        self.file_name = file_name

    async def process_element(self, element: ET.Element):
        tag = TagModel(name=element.tag, file_id=self.file_id)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        for attr_name, attr_value in element.attrib.items():
            attribute = AttributeModel(name=attr_name, value=attr_value, tag_id=tag.id)
            self.db.add(attribute)

        await self.db.commit()

        for child in element:
            await self.process_element(child)


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tag_count(self, file_name: str, tag_name: str) -> TagCountResponse:
        result = await self.db.execute(
            select(FileModel).filter(FileModel.name == file_name)
        )
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        result = await self.db.execute(
            select(TagModel).filter(
                TagModel.file_id == file.id, TagModel.name == tag_name
            )
        )
        count = len(result.scalars().all())

        if count == 0:
            raise HTTPException(
                status_code=404, detail="В файле отсутствует тег с данным названием"
            )

        return TagCountResponse(count=count)

    async def get_tag_attributes(
        self, file_name: str, tag_name: str
    ) -> TagAttributesResponse:
        result = await self.db.execute(
            select(FileModel).filter(FileModel.name == file_name)
        )
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        result = await self.db.execute(
            select(TagModel).filter(
                TagModel.file_id == file.id, TagModel.name == tag_name
            )
        )
        tags = result.scalars().all()

        if not tags:
            raise HTTPException(status_code=404, detail="Тег не найден")

        attribute_names = set()
        for tag in tags:
            result = await self.db.execute(
                select(AttributeModel).filter(AttributeModel.tag_id == tag.id)
            )
            for attr in result.scalars().all():
                attribute_names.add(attr.name)

        return TagAttributesResponse(attributes=list(attribute_names))
