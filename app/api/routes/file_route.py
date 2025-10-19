from fastapi import File, UploadFile, FastAPI, APIRouter
from typing import Annotated
import os

router = APIRouter(prefix="files", tags=["files"])

@router.post("/csv")
def create_csv_file(csv: Annotated[bytes, File()]):
    pass
