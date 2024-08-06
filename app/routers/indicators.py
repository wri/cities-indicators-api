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


@router.get("/indicators/{indicator_name}/{city_id}")
# Return one indicator value for one city top admin level from Carto
def get_city_indicator(indicator_name: str, city_id: str):
    city_indicator_df = read_carto(
        f"SELECT * FROM indicators WHERE indicator = '{indicator_name}' and geo_name = '{city_id}'"
    )
    # Object of type Timestamp is not JSON serializable. Need to convert to string first.
    city_indicator_df["creation_date"] = city_indicator_df["creation_date"].dt.strftime(
        "%Y-%m-%d"
    )
    city_indicator = json.loads(city_indicator_df.to_json())
    city_indicator = city_indicator["features"][0]["properties"]
    # Reorder and select city indicator fields
    desired_keys = [
        "geo_id",
        "geo_name",
        "geo_level",
        "geo_parent_name",
        "indicator",
        "value",
        "indicator_version",
    ]
    city_indicator = {
        key: city_indicator[key] for key in desired_keys if key in city_indicator
    }

    return {"indicator_values": city_indicator}
