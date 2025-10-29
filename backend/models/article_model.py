from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    doc = Column(String(50))
    titre = Column(String(255))
    chapitre = Column(String(255))
    section = Column(String(255))
    article = Column(String(50))
    contenu = Column(Text)
    pages = Column(String(50))
