"""
Synthetic Focus Group API for HUMANIST
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import asyncio
import httpx
from datetime import datetime

app = FastAPI(title="Synthetic Focus Group API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load personas
PERSONAS = json.loads('''
[
  {"id":1,"name":"Олена Коваленко","age":34,"gender":"female","city":"Київ","occupation":"IT Project Manager","income":"50000-75000","state_primary":"stress","state_secondary":"sleep","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"low","personality":"Аналітик, довіряє дослідженням. Працює в IT, стресує через дедлайни."},
  {"id":2,"name":"Андрій Мельник","age":42,"gender":"male","city":"Київ","occupation":"Власник бізнесу","income":"100000+","state_primary":"stress","state_secondary":"focus","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"very_low","personality":"Підприємець, цінує час, готовий платити за найкраще."},
  {"id":3,"name":"Марія Шевченко","age":28,"gender":"female","city":"Київ","occupation":"Маркетолог","income":"35000-50000","state_primary":"energy","state_secondary":"focus","lifestyle":"creative_professional","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Креативна, слідкує за трендами. Цікавиться CBD, але обережна."},
  {"id":4,"name":"Ігор Бондаренко","age":55,"gender":"male","city":"Київ","occupation":"Лікар","income":"50000-75000","state_primary":"sleep","state_secondary":"recovery","lifestyle":"wellness_enthusiast","cbd_experience":"experienced","price_sensitivity":"low","personality":"Лікар, скептик до непідтверджених заяв."},
  {"id":5,"name":"Катерина Ткаченко","age":38,"gender":"female","city":"Київ","occupation":"HR директор","income":"75000-100000","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"low","personality":"Відповідає за wellbeing команди."},
  {"id":6,"name":"Василь Петренко","age":67,"gender":"male","city":"Київ","occupation":"Пенсіонер","income":"20000-35000","state_primary":"sleep","state_secondary":"immunity","lifestyle":"conscious_consumer","cbd_experience":"beginner","price_sensitivity":"high","personality":"Консервативний, обережний."},
  {"id":7,"name":"Софія Литвиненко","age":22,"gender":"female","city":"Київ","occupation":"Студентка","income":"до 20000","state_primary":"focus","state_secondary":"stress","lifestyle":"biohacker","cbd_experience":"intermediate","price_sensitivity":"high","personality":"Gen Z, цікавиться біохакінгом."},
  {"id":8,"name":"Наталія Кравченко","age":45,"gender":"female","city":"Київ","occupation":"Бухгалтер","income":"35000-50000","state_primary":"stress","state_secondary":"sleep","lifestyle":"conscious_consumer","cbd_experience":"none","price_sensitivity":"medium","personality":"Скептик, але відкрита."},
  {"id":9,"name":"Олександр Савченко","age":31,"gender":"male","city":"Київ","occupation":"Frontend розробник","income":"75000-100000","state_primary":"focus","state_secondary":"energy","lifestyle":"biohacker","cbd_experience":"experienced","price_sensitivity":"low","personality":"Технар, оптимізує все."},
  {"id":10,"name":"Людмила Гончар","age":58,"gender":"female","city":"Київ","occupation":"Вчителька","income":"20000-35000","state_primary":"sleep","state_secondary":"stress","lifestyle":"holistic_believer","cbd_experience":"beginner","price_sensitivity":"high","personality":"Віддає перевагу натуральним засобам."},
  {"id":11,"name":"Дмитро Яременко","age":36,"gender":"male","city":"Київ","occupation":"Фінансовий аналітик","income":"75000-100000","state_primary":"stress","state_secondary":"focus","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Аналітик, порівнює варіанти."},
  {"id":12,"name":"Оксана Пономаренко","age":41,"gender":"female","city":"Київ","occupation":"Психолог","income":"50000-75000","state_primary":"stress","state_secondary":"recovery","lifestyle":"wellness_enthusiast","cbd_experience":"experienced","price_sensitivity":"low","personality":"Практикуючий психолог."},
  {"id":13,"name":"Артем Лисенко","age":24,"gender":"male","city":"Київ","occupation":"Контент-криейтор","income":"35000-50000","state_primary":"energy","state_secondary":"focus","lifestyle":"creative_professional","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Створює контент для брендів."},
  {"id":14,"name":"Ірина Москаленко","age":52,"gender":"female","city":"Київ","occupation":"Підприємець","income":"75000-100000","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"low","personality":"Власниця салону краси."},
  {"id":15,"name":"Богдан Кучер","age":29,"gender":"male","city":"Київ","occupation":"Фітнес-тренер","income":"35000-50000","state_primary":"recovery","state_secondary":"energy","lifestyle":"fitness_focused","cbd_experience":"experienced","price_sensitivity":"medium","personality":"Професійний тренер."},
  {"id":16,"name":"Вікторія Романенко","age":33,"gender":"female","city":"Київ","occupation":"Юрист","income":"75000-100000","state_primary":"stress","state_secondary":"sleep","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"low","personality":"Юрист, цінує прозорість."},
  {"id":17,"name":"Тетяна Федоренко","age":47,"gender":"female","city":"Київ","occupation":"Менеджер","income":"50000-75000","state_primary":"sleep","state_secondary":"stress","lifestyle":"conscious_consumer","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Проблеми зі сном."},
  {"id":18,"name":"Максим Поліщук","age":19,"gender":"male","city":"Київ","occupation":"Студент IT","income":"до 20000","state_primary":"focus","state_secondary":"energy","lifestyle":"biohacker","cbd_experience":"beginner","price_sensitivity":"very_high","personality":"Студент-айтішник."},
  {"id":19,"name":"Галина Захарченко","age":62,"gender":"female","city":"Київ","occupation":"Пенсіонерка","income":"20000-35000","state_primary":"immunity","state_secondary":"sleep","lifestyle":"holistic_believer","cbd_experience":"beginner","price_sensitivity":"high","personality":"Колишня медсестра."},
  {"id":20,"name":"Роман Ковальчук","age":39,"gender":"male","city":"Київ","occupation":"Архітектор","income":"50000-75000","state_primary":"focus","state_secondary":"stress","lifestyle":"creative_professional","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Архітектор, цінує дизайн."},
  {"id":21,"name":"Юлія Сидоренко","age":35,"gender":"female","city":"Львів","occupation":"IT рекрутер","income":"50000-75000","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Працює у львівській IT-компанії."},
  {"id":22,"name":"Михайло Гнатюк","age":48,"gender":"male","city":"Львів","occupation":"Підприємець","income":"50000-75000","state_primary":"energy","state_secondary":"stress","lifestyle":"wellness_enthusiast","cbd_experience":"experienced","price_sensitivity":"medium","personality":"Власник кав'ярні."},
  {"id":23,"name":"Анна Войтович","age":27,"gender":"female","city":"Львів","occupation":"Графічний дизайнер","income":"35000-50000","state_primary":"focus","state_secondary":"stress","lifestyle":"creative_professional","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Фрілансер-дизайнер."},
  {"id":24,"name":"Петро Левицький","age":56,"gender":"male","city":"Львів","occupation":"Викладач","income":"35000-50000","state_primary":"sleep","state_secondary":"focus","lifestyle":"conscious_consumer","cbd_experience":"none","price_sensitivity":"medium","personality":"Науковий скептик."},
  {"id":25,"name":"Христина Бойко","age":31,"gender":"female","city":"Львів","occupation":"Йога-інструктор","income":"20000-35000","state_primary":"recovery","state_secondary":"stress","lifestyle":"holistic_believer","cbd_experience":"experienced","price_sensitivity":"medium","personality":"Практикує йогу."},
  {"id":26,"name":"Віталій Демченко","age":44,"gender":"male","city":"Львів","occupation":"Менеджер з продажу","income":"50000-75000","state_primary":"stress","state_secondary":"sleep","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Багато подорожує."},
  {"id":27,"name":"Марина Павлюк","age":38,"gender":"female","city":"Львів","occupation":"Мама у декреті","income":"35000-50000","state_primary":"sleep","state_secondary":"stress","lifestyle":"conscious_consumer","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Мама маленької дитини."},
  {"id":28,"name":"Олександра Коцюба","age":23,"gender":"female","city":"Львів","occupation":"Бариста","income":"до 20000","state_primary":"energy","state_secondary":"focus","lifestyle":"creative_professional","cbd_experience":"beginner","price_sensitivity":"very_high","personality":"Цікавиться функціональними напоями."},
  {"id":29,"name":"Євген Дорошенко","age":51,"gender":"male","city":"Дніпро","occupation":"Інженер","income":"35000-50000","state_primary":"sleep","state_secondary":"recovery","lifestyle":"skeptic","cbd_experience":"none","price_sensitivity":"high","personality":"Прагматик, скептик."},
  {"id":30,"name":"Ольга Кузьменко","age":36,"gender":"female","city":"Дніпро","occupation":"Підприємець","income":"50000-75000","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Веде e-commerce бізнес."},
  {"id":31,"name":"Сергій Марченко","age":43,"gender":"male","city":"Дніпро","occupation":"Програміст","income":"75000-100000","state_primary":"focus","state_secondary":"stress","lifestyle":"biohacker","cbd_experience":"experienced","price_sensitivity":"low","personality":"Senior розробник."},
  {"id":32,"name":"Надія Остапенко","age":59,"gender":"female","city":"Дніпро","occupation":"Головний бухгалтер","income":"50000-75000","state_primary":"stress","state_secondary":"sleep","lifestyle":"conscious_consumer","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Стрес під час звітності."},
  {"id":33,"name":"Антон Шевчук","age":26,"gender":"male","city":"Дніпро","occupation":"Спортсмен MMA","income":"35000-50000","state_primary":"recovery","state_secondary":"sleep","lifestyle":"fitness_focused","cbd_experience":"experienced","price_sensitivity":"medium","personality":"Професійний боєць."},
  {"id":34,"name":"Валентина Козак","age":64,"gender":"female","city":"Дніпро","occupation":"Пенсіонерка","income":"до 20000","state_primary":"sleep","state_secondary":"immunity","lifestyle":"holistic_believer","cbd_experience":"none","price_sensitivity":"very_high","personality":"Обмежений бюджет."},
  {"id":35,"name":"Лариса Мельниченко","age":40,"gender":"female","city":"Одеса","occupation":"Ресторатор","income":"75000-100000","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"low","personality":"Власниця ресторану."},
  {"id":36,"name":"Олексій Грищенко","age":33,"gender":"male","city":"Одеса","occupation":"Моряк","income":"100000+","state_primary":"sleep","state_secondary":"stress","lifestyle":"conscious_consumer","cbd_experience":"intermediate","price_sensitivity":"low","personality":"Працює на судні."},
  {"id":37,"name":"Карина Іванова","age":29,"gender":"female","city":"Одеса","occupation":"SMM-менеджер","income":"35000-50000","state_primary":"focus","state_secondary":"stress","lifestyle":"creative_professional","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Працює з соцмережами."},
  {"id":38,"name":"Віктор Черненко","age":57,"gender":"male","city":"Одеса","occupation":"Капітан порту","income":"50000-75000","state_primary":"sleep","state_secondary":"recovery","lifestyle":"skeptic","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Колишній моряк."},
  {"id":39,"name":"Аліна Коломієць","age":45,"gender":"female","city":"Харків","occupation":"Викладач англійської","income":"35000-50000","state_primary":"stress","state_secondary":"focus","lifestyle":"conscious_consumer","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Живе в Харкові, стрес через війну."},
  {"id":40,"name":"Денис Савчук","age":37,"gender":"male","city":"Харків","occupation":"IT-менеджер","income":"75000-100000","state_primary":"stress","state_secondary":"sleep","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"low","personality":"Керує IT-командою."},
  {"id":41,"name":"Олена Кравчук","age":52,"gender":"female","city":"Харків","occupation":"Медсестра","income":"20000-35000","state_primary":"sleep","state_secondary":"stress","lifestyle":"holistic_believer","cbd_experience":"beginner","price_sensitivity":"high","personality":"Працює в лікарні."},
  {"id":42,"name":"Юлія Данилюк","age":30,"gender":"female","city":"Вінниця","occupation":"Фармацевт","income":"35000-50000","state_primary":"energy","state_secondary":"focus","lifestyle":"wellness_enthusiast","cbd_experience":"experienced","price_sensitivity":"medium","personality":"Працює в аптеці."},
  {"id":43,"name":"Павло Тимченко","age":46,"gender":"male","city":"Вінниця","occupation":"Фермер","income":"50000-75000","state_primary":"recovery","state_secondary":"sleep","lifestyle":"conscious_consumer","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Фізично важка робота."},
  {"id":44,"name":"Світлана Бондар","age":54,"gender":"female","city":"Полтава","occupation":"Директор школи","income":"50000-75000","state_primary":"stress","state_secondary":"sleep","lifestyle":"conscious_consumer","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Керує школою."},
  {"id":45,"name":"Ігор Ніколаєнко","age":28,"gender":"male","city":"Полтава","occupation":"Ветеринар","income":"35000-50000","state_primary":"stress","state_secondary":"energy","lifestyle":"wellness_enthusiast","cbd_experience":"intermediate","price_sensitivity":"medium","personality":"Цікавиться CBD."},
  {"id":46,"name":"Марія Герасименко","age":68,"gender":"female","city":"Чернігів","occupation":"Пенсіонерка","income":"до 20000","state_primary":"sleep","state_secondary":"immunity","lifestyle":"holistic_believer","cbd_experience":"none","price_sensitivity":"very_high","personality":"Пережила окупацію."},
  {"id":47,"name":"Андрій Коваль","age":35,"gender":"male","city":"Чернівці","occupation":"Митний брокер","income":"75000-100000","state_primary":"stress","state_secondary":"focus","lifestyle":"high_achiever","cbd_experience":"experienced","price_sensitivity":"low","personality":"Знає про легальність CBD."},
  {"id":48,"name":"Тетяна Шульга","age":42,"gender":"female","city":"Черкаси","occupation":"Бухгалтер ФОП","income":"35000-50000","state_primary":"stress","state_secondary":"sleep","lifestyle":"conscious_consumer","cbd_experience":"beginner","price_sensitivity":"medium","personality":"Стрес під час звітності."},
  {"id":49,"name":"Роман Іваненко","age":50,"gender":"male","city":"Суми","occupation":"Директор заводу","income":"100000+","state_primary":"stress","state_secondary":"energy","lifestyle":"high_achiever","cbd_experience":"intermediate","price_sensitivity":"very_low","personality":"Керує підприємством."},
  {"id":50,"name":"Ганна Литвин","age":37,"gender":"female","city":"Житомир","occupation":"Вчителька","income":"20000-35000","state_primary":"stress","state_secondary":"energy","lifestyle":"holistic_believer","cbd_experience":"beginner","price_sensitivity":"high","personality":"Працює з дітьми."}
]
''')

# Models
class HypothesisRequest(BaseModel):
    hypothesis: str
    question_type: str = "scale"  # scale, choice
    options: Optional[List[str]] = None
    segments: Optional[Dict[str, List[str]]] = None

class TestResult(BaseModel):
    id: str
    hypothesis: str
    created_at: str
    results: Dict[str, Any]

# Storage (in production use PostgreSQL)
test_results: List[Dict] = []

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

async def query_claude(persona: dict, hypothesis: str, question_type: str, options: List[str] = None) -> dict:
    """Query Claude API as a specific persona"""
    
    if not ANTHROPIC_API_KEY:
        # Fallback to rule-based simulation
        return simulate_response(persona, hypothesis, question_type, options)
    
    system_prompt = f"""Ти — {persona['name']}, {persona['age']} років, {persona['gender']}, живеш у місті {persona['city']}.

Твій профіль:
- Професія: {persona['occupation']}
- Дохід: {persona['income']} грн/міс
- Головна проблема зі здоров'ям: {persona['state_primary']}
- Досвід з CBD: {persona['cbd_experience']}
- Чутливість до ціни: {persona['price_sensitivity']}
- Характер: {persona['personality']}

Відповідай ТІЛЬКИ від імені цієї людини. Будь чесним. Українською мовою."""

    if question_type == "scale":
        user_prompt = f"""Питання: {hypothesis}

Оціни за шкалою від 1 до 10:
1 = категорично не згоден / зовсім не цікаво
10 = повністю згоден / дуже цікаво

Відповідь ТІЛЬКИ у форматі JSON: {{"score": число, "reasoning": "1 речення чому"}}"""
    else:
        user_prompt = f"""Питання: {hypothesis}

Варіанти:
{chr(10).join([f"{i+1}. {opt}" for i, opt in enumerate(options or [])])}

Відповідь ТІЛЬКИ у форматі JSON: {{"choice": номер, "reasoning": "1 речення чому"}}"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 150,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["content"][0]["text"]
                # Parse JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', text)
                if json_match:
                    result = json.loads(json_match.group())
                    result["persona_id"] = persona["id"]
                    result["persona_name"] = persona["name"]
                    return result
    except Exception as e:
        print(f"Claude API error: {e}")
    
    return simulate_response(persona, hypothesis, question_type, options)


def simulate_response(persona: dict, hypothesis: str, question_type: str, options: List[str] = None) -> dict:
    """Rule-based simulation when API is not available"""
    import random
    
    hypothesis_lower = hypothesis.lower()
    
    price_high = persona["price_sensitivity"] in ["very_high", "high"]
    price_low = persona["price_sensitivity"] in ["low", "very_low"]
    experienced = persona["cbd_experience"] == "experienced"
    beginner = persona["cbd_experience"] in ["beginner", "none"]
    young = persona["age"] < 35
    older = persona["age"] >= 50
    kyiv = persona["city"] == "Київ"
    
    if question_type == "scale":
        base_score = 5.5
        
        # Price/discount mentions
        if "знижк" in hypothesis_lower or "акці" in hypothesis_lower or "ціна" in hypothesis_lower:
            if price_high: base_score += 2.5
            if price_low: base_score -= 0.5
        
        # Subscription
        if "підписк" in hypothesis_lower:
            if experienced: base_score += 1.5
            if beginner: base_score -= 1.5
            if young: base_score += 1
            if older: base_score -= 1
        
        # Experience Center / store
        if "experience" in hypothesis_lower or "магазин" in hypothesis_lower or "офлайн" in hypothesis_lower:
            if kyiv: base_score += 2
            else: base_score -= 1.5
        
        # New product
        if "новий" in hypothesis_lower or "продукт" in hypothesis_lower:
            if experienced: base_score += 0.5
            if beginner: base_score += 1.5
        
        # Sleep related
        if "сон" in hypothesis_lower or "sleep" in hypothesis_lower:
            if persona["state_primary"] == "sleep": base_score += 2
        
        # Stress related  
        if "стрес" in hypothesis_lower or "stress" in hypothesis_lower:
            if persona["state_primary"] == "stress": base_score += 2
        
        # Focus related
        if "фокус" in hypothesis_lower or "концентрац" in hypothesis_lower:
            if persona["state_primary"] == "focus": base_score += 2
        
        # Random factor
        random_factor = (random.random() - 0.5) * 2.5
        score = round(base_score + random_factor)
        score = max(1, min(10, score))
        
        return {
            "score": score,
            "reasoning": "Симульована відповідь на основі профілю",
            "persona_id": persona["id"],
            "persona_name": persona["name"]
        }
    
    else:  # choice
        if not options:
            return {"choice": 1, "persona_id": persona["id"], "persona_name": persona["name"]}
        
        weights = [1.0] * len(options)
        
        for i, opt in enumerate(options):
            opt_lower = opt.lower()
            if ("дорог" in opt_lower or "премі" in opt_lower) and price_low:
                weights[i] += 2
            if ("дешев" in opt_lower or "економ" in opt_lower or "бюджет" in opt_lower) and price_high:
                weights[i] += 2
            if ("підписк" in opt_lower) and experienced:
                weights[i] += 1.5
        
        total = sum(weights)
        r = random.random() * total
        cumulative = 0
        choice_idx = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative:
                choice_idx = i
                break
        
        return {
            "choice": choice_idx + 1,
            "choice_text": options[choice_idx],
            "reasoning": "Симульована відповідь",
            "persona_id": persona["id"],
            "persona_name": persona["name"]
        }


@app.get("/api/health")
async def health():
    return {"status": "ok", "personas": len(PERSONAS)}


@app.get("/api/personas")
async def get_personas():
    return {"personas": PERSONAS, "total": len(PERSONAS)}


@app.get("/api/segments")
async def get_segments():
    states = list(set(p["state_primary"] for p in PERSONAS))
    lifestyles = list(set(p["lifestyle"] for p in PERSONAS))
    cities = list(set(p["city"] for p in PERSONAS))
    
    return {
        "states": states,
        "lifestyles": lifestyles,
        "cities": cities,
        "state_labels": {
            "stress": "Стрес", "sleep": "Сон", "energy": "Енергія",
            "focus": "Фокус", "immunity": "Імунітет", "recovery": "Відновлення"
        },
        "lifestyle_labels": {
            "high_achiever": "High Achievers", "creative_professional": "Креативні",
            "biohacker": "Біохакери", "wellness_enthusiast": "Wellness",
            "fitness_focused": "Фітнес", "holistic_believer": "Холістики",
            "conscious_consumer": "Свідомі споживачі", "skeptic": "Скептики"
        }
    }


@app.post("/api/test")
async def run_test(request: HypothesisRequest):
    # Filter personas
    filtered = PERSONAS.copy()
    
    if request.segments:
        if request.segments.get("state"):
            filtered = [p for p in filtered if p["state_primary"] in request.segments["state"]]
        if request.segments.get("lifestyle"):
            filtered = [p for p in filtered if p["lifestyle"] in request.segments["lifestyle"]]
        if request.segments.get("city"):
            filtered = [p for p in filtered if p["city"] in request.segments["city"]]
    
    if not filtered:
        raise HTTPException(status_code=400, detail="No personas match filters")
    
    # Run queries (parallel)
    tasks = [
        query_claude(p, request.hypothesis, request.question_type, request.options)
        for p in filtered
    ]
    responses = await asyncio.gather(*tasks)
    
    # Aggregate results
    if request.question_type == "scale":
        scores = [r["score"] for r in responses if "score" in r]
        avg = sum(scores) / len(scores) if scores else 0
        
        distribution = [0] * 10
        for s in scores:
            distribution[s - 1] += 1
        
        by_state = {}
        by_lifestyle = {}
        for r, p in zip(responses, filtered):
            state = p["state_primary"]
            lifestyle = p["lifestyle"]
            score = r.get("score", 5)
            
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(score)
            
            if lifestyle not in by_lifestyle:
                by_lifestyle[lifestyle] = []
            by_lifestyle[lifestyle].append(score)
        
        results = {
            "type": "scale",
            "total": len(responses),
            "average": round(avg, 1),
            "distribution": [{"score": i+1, "count": c, "pct": round(c/len(scores)*100, 1)} for i, c in enumerate(distribution)],
            "positive": len([s for s in scores if s >= 7]),
            "neutral": len([s for s in scores if 4 <= s < 7]),
            "negative": len([s for s in scores if s < 4]),
            "by_state": [{"state": k, "avg": round(sum(v)/len(v), 1), "count": len(v)} for k, v in by_state.items()],
            "by_lifestyle": [{"lifestyle": k, "avg": round(sum(v)/len(v), 1), "count": len(v)} for k, v in by_lifestyle.items()],
            "responses": responses[:10]  # Sample
        }
    else:
        choice_counts = {}
        for r in responses:
            choice = r.get("choice_text", r.get("choice", "Unknown"))
            choice_counts[choice] = choice_counts.get(choice, 0) + 1
        
        results = {
            "type": "choice",
            "total": len(responses),
            "choices": [{"choice": k, "count": v, "pct": round(v/len(responses)*100, 1)} for k, v in choice_counts.items()],
            "responses": responses[:10]
        }
    
    # Store result
    test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_record = {
        "id": test_id,
        "hypothesis": request.hypothesis,
        "created_at": datetime.now().isoformat(),
        "results": results
    }
    test_results.append(test_record)
    
    return test_record


@app.get("/api/results")
async def get_results():
    return {"results": test_results}


# Serve frontend in production
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
