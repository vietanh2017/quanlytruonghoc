# modules/thi_dua_hoc_sinh/repository/base_repository.py
from typing import Optional, List, TypeVar, Generic
from sqlalchemy.orm import Session
from core.db.base import Base

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model_class: T):
        self.session = session
        self.model = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, **filters) -> List[T]:
        query = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def create(self, **data) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, id: int, **data) -> Optional[T]:
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                if value is not None:
                    setattr(obj, key, value)
            self.session.flush()
        return obj
    
    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False