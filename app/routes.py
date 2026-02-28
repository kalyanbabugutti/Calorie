import shutil
import os
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .model import predict_image

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Nutrition data (no database)
NUTRITION_DATA = {
    "Banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    "Apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    "Pizza": {"calories": 266, "protein": 11, "carbs": 33, "fat": 10},
    "Cheeseburger": {"calories": 295, "protein": 17, "carbs": 30, "fat": 14},
    "Hotdog": {"calories": 290, "protein": 11, "carbs": 4, "fat": 26},
    "Orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fat": 0.1},
    "Broccoli": {"calories": 55, "protein": 3.7, "carbs": 11, "fat": 0.6},
    "Carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
}

FOOD_MAPPING = {
    "banana": "Banana",
    "pizza": "Pizza",
    "cheeseburger": "Cheeseburger",
    "hotdog": "Hotdog",
    "apple": "Apple",
    "orange": "Orange",
    "broccoli": "Broccoli",
    "carrot": "Carrot",
}


def calculate_health_score(calories, protein, fat):
    score = 100
    if calories > 300:
        score -= 20
    if fat > 20:
        score -= 15
    if protein < 5:
        score -= 10
    return score


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, file: UploadFile = File(...)):
    os.makedirs("static", exist_ok=True)

    file_path = f"static/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prediction = predict_image(file_path).lower()
    print("PREDICTED:", prediction)

    matched_food = None
    for key in FOOD_MAPPING:
        if key in prediction:
            matched_food = FOOD_MAPPING[key]
            break

    if not matched_food:
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": "Food not recognized."},
        )

    data = NUTRITION_DATA[matched_food]

    calories = data["calories"]
    protein = data["protein"]
    carbs = data["carbs"]
    fat = data["fat"]

    score = calculate_health_score(calories, protein, fat)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "image": file.filename,
            "food": matched_food,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "score": score,
        },
    )