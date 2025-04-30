import copy


def cleanup_spaces_in_response(response_dict: dict) -> dict:
    response_dict_copy = copy.deepcopy(response_dict)
    for k, v in response_dict_copy.items():
        if isinstance(v, str):
            response_dict[k] = v.strip()
        elif isinstance(v, list):
            for idx, list_val in enumerate(v):
                if isinstance(list_val, str):
                    response_dict[k][idx] = list_val.strip()
        elif isinstance(v, dict):
            vcopy = copy.deepcopy(v)
            for subk, subv in vcopy.items():
                if isinstance(subv, str):
                    response_dict[k][subk] = subv.strip()
    return response_dict
