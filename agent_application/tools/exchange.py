import requests


def exchange_rate(base: str, target: str):
    url = "https://api.frankfurter.dev/v1/latest"

    params = {
        "base": base,
        "symbols": target,
    }

    response = requests.get(
        url,
        params=params,
    )

    response.raise_for_status()

    data = response.json()

    rate = data["rates"][target]

    return {
        "base": data["base"],
        "target": target,
        "date": data["date"],
        "rate": rate,
    }