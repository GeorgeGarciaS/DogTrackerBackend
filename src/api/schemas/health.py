from pydantic import BaseModel

"""
    Request Schemass
"""

"""
    Public Schemas
"""
class HealthResponse(BaseModel):
    status: str

"""
    Internal Schemas
"""