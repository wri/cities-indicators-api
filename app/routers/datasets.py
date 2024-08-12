from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.datasets import LIST_DATASETS_RESPONSES
from app.services import datasets as datasets_service

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
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return {"datasets": datasets}
