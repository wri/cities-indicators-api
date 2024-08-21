from fastapi import HTTPException, Request


def validate_query_params(*params: str):
    def dependency(request: Request):
        for param in request.query_params:
            if param not in params:
                raise HTTPException(
                    status_code=400, detail=f"Invalid query parameter: {param}"
                )

    return dependency
