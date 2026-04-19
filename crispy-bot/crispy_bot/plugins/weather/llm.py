import litellm


# Give the result of the llm
async def read(prompt: str,
                    llm_provider: str,
                    llm_model_name: str,
                    llm_base_url: str,
                    llm_api_key: str) -> str:
    response = await litellm.acompletion(
        model=f"{llm_provider}/{llm_model_name}",
        base_url=llm_base_url,
        api_key=llm_api_key,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content


# Read the result of real-time weather
async def read_real_weather(
        weather_result,
        position,
        llm_provider: str,
        llm_model_name: str,
        llm_base_url: str,
        llm_api_key: str
):
    prompt = \
f"""
你是人工智能助手Crispy，你需要用轻松活泼的语气说明以下信息(**不要遗漏任何关键信息!**)，
你可以适当使用喵或者emoji来提高语气的亲和性，但不要加太多，容易让用户觉得烦，并且你可以给出对当前天气的评价以及给用户的建议
注意你只回一段对话，所以说不要加"还有什么要问的"这样的话语在你的回答的最后面。
**你的前端不支持markdown语法解析，所以不要使用MD格式回答内容!**
# {position}天气
- 实际温度: {weather_result["now"]["temp"]}摄氏度
- 体感温度: {weather_result["now"]["feelsLike"]}摄氏度
- 天气状况: {weather_result["now"]["text"]}
- 风向: {weather_result["now"]["windDir"]}
- 风速: {weather_result["now"]["windSpeed"]}公里/小时
- 风力等级: {weather_result["now"]["windScale"]}
    (采用蒲福风级，具体含义看后文)
- 相对湿度: {weather_result["now"]["humidity"]}%
- 过去一小时降水量: {weather_result["now"]["precip"]}毫米
- 能见度: {weather_result["now"]["vis"]}公里
# 参考信息
- **蒲福风级 0**
  - 术语(ZH): 无风
  - 术语(EN): Calm
  - 风速: < 1 knot / < 1 mph / < 2 km/h / < 0.5 m/s
  - 浪高: 0 m
  - 海上情况: 平静
  - 陆上情况: 静,烟直上
- **蒲福风级 1**
  - 术语(ZH): 软风
  - 术语(EN): Light air
  - 风速: 1–3 knots / 1–3 mph / 2–5 km/h / 0.5–1.5 m/s
  - 浪高: 0.1 m
  - 海上情况: 微波峰无飞沫
  - 陆上情况: 烟示风向
- **蒲福风级 2**
  - 术语(ZH): 轻风
  - 术语(EN): Light breeze
  - 风速: 4–6 knots / 4–7 mph / 6–11 km/h / 1.6–3.3 m/s
  - 浪高: 0.2–0.5 m
  - 海上情况: 小波峰未破碎
  - 陆上情况: 感觉有风
- **蒲福风级 3**
  - 术语(ZH): 微风
  - 术语(EN): Gentle breeze
  - 风速: 7–10 knots / 8–12 mph / 12–19 km/h / 3.4–5.5 m/s
  - 浪高: 0.6–1.0 m
  - 海上情况: 小波峰顶破裂
  - 陆上情况: 旌旗展开
- **蒲福风级 4**
  - 术语(ZH): 和风
  - 术语(EN): Moderate breeze
  - 风速: 11–16 knots / 13–18 mph / 20–28 km/h / 5.5–7.9 m/s
  - 浪高: 1.0-1.5 m
  - 海上情况: 小浪白沫波峰
  - 陆上情况: 吹起尘土
- **蒲福风级 5**
  - 术语(ZH): 清风
  - 术语(EN): Fresh breeze
  - 风速: 17–21 knots / 19–24 mph / 29–38 km/h / 8–10.7 m/s
  - 浪高: 2.0–2.5 m
  - 海上情况: 中浪折沫峰群
  - 陆上情况: 小树摇摆
- **蒲福风级 6**
  - 术语(ZH): 强风
  - 术语(EN): Strong breeze
  - 风速: 22–27 knots / 25–31 mph / 39–49 km/h / 10.8–13.8 m/s
  - 浪高: 3.0–4.0 m
  - 海上情况: 大浪白沫离峰
  - 陆上情况: 电线有声
- **蒲福风级 7**
  - 术语(ZH): 疾风
  - 术语(EN): Near gale
  - 风速: 28–33 knots / 32–38 mph / 50–61 km/h / 13.9–17.1 m/s
  - 浪高: 4.0–5.5 m
  - 海上情况: 破峰白沫成条
  - 陆上情况: 步行困难
- **蒲福风级 8**
  - 术语(ZH): 大风
  - 术语(EN): Gale
  - 风速: 34–40 knots / 39–46 mph / 62–74 km/h / 17.2–20.7 m/s
  - 浪高: 5.5–7.5 m
  - 海上情况: 浪长高有浪花
  - 陆上情况: 折毁树枝
- **蒲福风级 9**
  - 术语(ZH): 烈风
  - 术语(EN): Strong gale
  - 风速: 41–47 knots / 47–54 mph / 75–88 km/h / 20.8–24.4 m/s
  - 浪高: 7.0–10.0 m
  - 海上情况: 浪峰倒卷
  - 陆上情况: 小损房屋
- **蒲福风级 10**
  - 术语(ZH): 狂风
  - 术语(EN): Storm
  - 风速: 48–55 knots / 55–63 mph / 89–102 km/h / 24.5–28.4 m/s
  - 浪高: 9.0–12.5 m
  - 海上情况: 海浪翻滚咆哮
  - 陆上情况: 拔起树木
- **蒲福风级 11**
  - 术语(ZH): 暴风
  - 术语(EN): Violent storm
  - 风速: 56–63 knots / 64–72 mph / 103–117 km/h / 28.5–32.6 m/s
  - 浪高: 11.5–16.0 m
  - 海上情况: 波峰全呈飞沫
  - 陆上情况: 损毁重大
- **蒲福风级 12**
  - 术语(ZH): 飓风
  - 术语(EN): Hurricane
  - 风速: ≥ 64 knots / ≥ 73 mph / ≥ 118 km/h / ≥ 32.7 m/s
  - 浪高: ≥ 14.0 m
  - 海上情况: 海浪滔天
  - 陆上情况: 摧毁极大
- **蒲福风级 13** (扩展)
  - 风速: 72–80 knots / 134-149 km/h / 37.0-41.4 m/s
  - 浪高: >14 m
  - 对应台风等级: 台风 TY
- **蒲福风级 14** (扩展)
  - 风速: 81–89 knots / 150-166 km/h / 41.5-46.1 m/s
  - 浪高: >14 m
  - 对应台风等级: 强台风 STY
- **蒲福风级 15** (扩展)
  - 风速: 90–99 knots / 167-183 km/h / 46.2-50.9 m/s
  - 浪高: >14 m
  - 对应台风等级: 强台风 STY
- **蒲福风级 16** (扩展)
  - 风速: 100–108 knots / 184-201 km/h / 51.0-56.0 m/s
  - 浪高: >14 m
  - 对应台风等级: 超强台风 SuperTY
- **蒲福风级 17** (扩展)
  - 风速: 109–119 knots / 202-220 km/h / 56.1-61.2 m/s
  - 浪高: >14 m
  - 对应台风等级: 超强台风 SuperTY
- **蒲福风级 >17** (扩展)
  - 风速: ≧120 knots / ≥221 km/h / ≥61.3 m/s
  - 浪高: >14 m
  - 对应台风等级: 超强台风 SuperTY
"""
    result = await read(
        prompt=prompt,
        llm_provider=llm_provider,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        llm_model_name=llm_model_name
    )
    return result
