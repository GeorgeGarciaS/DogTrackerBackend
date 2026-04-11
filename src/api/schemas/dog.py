from pydantic import BaseModel


class Dog(BaseModel):
    id: int
    name: str
    breed: str
    age: int

class DogsResponse(BaseModel):
    dogs: list[Dog]

class DogCreateRequest(BaseModel):
    name: str
    breed: str
    age: int