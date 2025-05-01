import copy


def cleanup_spaces_in_response(response: dict | list) -> dict | list:

    response_copy = copy.deepcopy(response)
    if isinstance(response, list):
        response_copy = enumerate(response_copy)
    elif isinstance(response, dict):
        response_copy = response.items()
    for k, v in response_copy:
        if isinstance(v, str):
            response[k] = v.strip()
        elif isinstance(v, list):
            for idx, list_val in enumerate(v):
                if isinstance(list_val, str):
                    response[k][idx] = list_val.strip()
        elif isinstance(v, dict):
            vcopy = copy.deepcopy(v)
            for subk, subv in vcopy.items():
                if isinstance(subv, str):
                    response[k][subk] = subv.strip()
    return response
