
from groq import Groq

from agent_application.basic_agent import MODEL
from agent_application.tools.weather import current_weather


client = Groq()


# =========================
# Step 1: Get Weather
# =========================

def get_weather_step(city: str):
    print("\n========== Step 1: Get Weather ==========")

    weather_result = current_weather(city)

    print("Weather Result:")
    print(weather_result)

    if not weather_result["success"]:
        raise RuntimeError(
            f"Weather query failed: {weather_result['error']}"
        )

    return weather_result["data"]


# =========================
# Step 2: Analyze Weather
# =========================

def analyze_weather_step(weather_data: dict):
    print("\n========== Step 2: Analyze Weather ==========")

    prompt = (
        "根据下面的天气数据，分析今天适合进行什么类型的活动。"
        "请简要说明理由，不要编造天气数据。\n\n"
        f"天气数据：{weather_data}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个实用的天气与活动分析助手。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    analysis_result = response.choices[0].message.content

    print("Analysis Result:")
    print(analysis_result)

    return analysis_result


# =========================
# Step 3: Generate Recommendation
# =========================

def generate_recommendation_step(
    weather_data: dict,
    analysis_result: str,
):
    print("\n========== Step 3: Generate Recommendation ==========")

    prompt = (
        "请根据天气数据和分析结果，为用户生成今天的活动建议。"
        "给出 2 到 3 条具体建议，并简要说明理由。"
        "不要编造天气数据。\n\n"
        f"天气数据：{weather_data}\n\n"
        f"分析结果：{analysis_result}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个实用的日常活动建议助手。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    final_answer = response.choices[0].message.content

    print("Final Answer:")
    print(final_answer)

    return final_answer


# =========================
# Multi-step Execution
# =========================

def run_multi_step_agent(city: str):
    print("========== Multi-step Agent ==========")

    # Step 1
    weather_data = get_weather_step(city)

    # Step 2
    analysis_result = analyze_weather_step(weather_data)

    # Step 3
    final_answer = generate_recommendation_step(
        weather_data,
        analysis_result,
    )

    return final_answer


# =========================
# Main
# =========================

if __name__ == "__main__":
    result = run_multi_step_agent("Tokyo")

    print("\n========== Completed ==========")
    print(result)