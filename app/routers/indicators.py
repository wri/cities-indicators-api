from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_expected_params
from app.responses.indicators import LIST_INDICATORS_RESPONSES
from app.services import indicators as indicators_service

router = APIRouter()


@router.get(
    "",
    dependencies=[Depends(get_expected_params("project"))],
    responses=LIST_INDICATORS_RESPONSES,
)
# Return all indicators metadata from Airtable
def list_indicators(project: str = Query(None, description="Project ID")):
    try:
        indicators_list = indicators_service.list_indicators(project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    if not indicators_list:
        raise HTTPException(status_code=404, detail="No indicators found.")

    return {"indicators": indicators_list}


@router.get("/indicators/{indicator_name}")
# Return one indicator values for all cities top admin level from Carto
def get_indicator(indicator_name: str):
    try:
        indicators_list = indicators_service.get_indicator(indicator_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e

    return {"indicator_values": indicators_list}
