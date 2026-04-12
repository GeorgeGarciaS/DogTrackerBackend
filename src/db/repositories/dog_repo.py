from sqlalchemy.orm import Session

from src.db.models.dog import DogModel


def create_dog_record(dog: DogModel, db: Session):
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return dog

def get_dog_by_id(dog_id: str, db: Session) -> DogModel | None:
    return db.query(DogModel).filter(DogModel.dog_id == dog_id).first()

def get_dog_records(db: Session) -> list[DogModel]:
    return db.query(DogModel).order_by(DogModel.created_at.desc()).all()
