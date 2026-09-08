from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.dependencies import get_db
from backend.app.services.sync_engine import sync_local_records


router = APIRouter(
    prefix="/sync",
    tags=["sync"],
)


@router.post("/")
def sync_records(
    db: Session = Depends(get_db),
):
    """
    Sync locally stored offline records.
    """

    summary = sync_local_records(db)

    return {
        "status": "success",
        "message": "Local records synced successfully.",
        "synced_records": summary,
    }