import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.datasets import LIST_DATASETS_RESPONSES
from app.services import datasets as datasets_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(get_expected_params("city_id"))],
    responses=LIST_DATASETS_RESPONSES,
)
def list_datasets(
    city_id: str = Query(None, description="City ID"),
):
    """
    Retrieve the list of datasets
    """
    try:
        datasets = datasets_service.list_datasets(city_id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred: Retrieving the list of datasets failed.",
        ) from e
    return {"datasets": datasets}
