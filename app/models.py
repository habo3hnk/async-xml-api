from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy import Integer, String, ForeignKey


Base = declarative_base()


class FileModel(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class TagModel(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("files.id"))


class AttributeModel(Base):
    __tablename__ = "attributes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[int] = mapped_column(String)
    value: Mapped[str] = mapped_column(String)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"))
