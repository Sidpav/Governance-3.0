def get_missing_fields(data):

    missing = []

    for key, value in data.items():

        if value is None:

            missing.append(key)

            continue

        if str(value).strip() == "":

            missing.append(key)

            continue

        if str(value).strip().lower() in [

            "none",
            "null",
            "n/a"

        ]:

            missing.append(key)

    return missing