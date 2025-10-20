from fastapi import File, APIRouter
from typing import Annotated

router = APIRouter(prefix="files", tags=["files"])


@router.post("/csv")
def create_csv_file(csv: Annotated[bytes, File()]):
    pass
