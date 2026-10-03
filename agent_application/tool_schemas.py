current_weather_schema = {
    "type": "function",
    "function": {
        "name": "current_weather",
        "description": "Get the current weather of a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name.",
                },
            },
            "required": ["city"],
        },
    },
}


exchange_rate_schema = {
    "type": "function",
    "function": {
        "name": "exchange_rate",
        "description": (
            "Get the latest exchange rate between two currencies."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "base": {
                    "type": "string",
                    "description": "The base currency code, such as USD.",
                },
                "target": {
                    "type": "string",
                    "description": "The target currency code, such as EUR.",
                },
            },
            "required": ["base", "target"],
        },
    },
}


tool_schemas = [
    current_weather_schema,
    exchange_rate_schema,
]