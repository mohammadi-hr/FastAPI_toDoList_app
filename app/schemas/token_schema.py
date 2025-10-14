from pydantic import BaseModel


class TokenBaseSchema(BaseModel):
    token: str
