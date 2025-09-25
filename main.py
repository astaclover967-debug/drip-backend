from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io
import os

app = FastAPI()

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MediaPipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

@app.post("/virtual-try-on")
async def virtual_try_on(user_image: UploadFile = File(...), clothing_image: UploadFile = File(...)):
    try:
        # Read images
        user_img_data = await user_image.read()
        clothing_img_data = await clothing_image.read()
        
        # Convert to OpenCV format
        user_np = np.frombuffer(user_img_data, np.uint8)
        user_img = cv2.imdecode(user_np, cv2.IMREAD_COLOR)
        
        clothing_np = np.frombuffer(clothing_img_data, np.uint8)
        clothing_img = cv2.imdecode(clothing_np, cv2.IMREAD_COLOR)
        
        # Body detection with MediaPipe
        user_img_rgb = cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB)
        results = pose.process(user_img_rgb)
        
        if not results.pose_landmarks:
            return JSONResponse({"error": "No body detected"}, status_code=400)
        
        # Get body coordinates for virtual try-on
        landmarks = results.pose_landmarks.landmark
        h, w = user_img.shape[:2]
        
        # Simple clothing overlay (basic version)
        result_img = overlay_clothing(user_img, clothing_img, landmarks, w, h)
        
        # Convert back to bytes
        _, buffer = cv2.imencode('.jpg', result_img)
        result_base64 = base64.b64encode(buffer).decode()
        
        return JSONResponse({
            "success": True,
            "try_on_image": result_base64,
            "message": "Virtual try-on completed"
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/analyze-weather")
async def analyze_weather(lat: float, lon: float):
    # OpenWeatherMap API
    api_key = "your_openweather_api_key"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    weather_data = response.json()
    
    return JSONResponse({
        "temperature": weather_data['main']['temp'],
        "condition": weather_data['weather'][0]['main'],
        "recommendation": get_weather_recommendation(weather_data['main']['temp'])
    })

@app.post("/suggest-outfit")
async def suggest_outfit(weather_data: dict, style: str = "casual"):
    # AI outfit suggestion logic
    suggestion = generate_outfit_suggestion(weather_data, style)
    return JSONResponse({"suggestion": suggestion})

def overlay_clothing(user_img, clothing_img, landmarks, width, height):
    # Basic clothing overlay logic
    # Get shoulder and hip points for positioning
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    
    # Calculate position and scale
    shoulder_width = abs(right_shoulder.x - left_shoulder.x) * width
    clothing_resized = cv2.resize(clothing_img, (int(shoulder_width * 1.5), int(shoulder_width * 2)))
    
    # Position clothing on body
    x = int(left_shoulder.x * width - shoulder_width * 0.2)
    y = int(left_shoulder.y * height)
    
    # Simple overlay (replace with proper blending)
    result = user_img.copy()
    result[y:y+clothing_resized.shape[0], x:x+clothing_resized.shape[1]] = clothing_resized
    
    return result

def get_weather_recommendation(temp):
    if temp < 10: return "Wear heavy jacket and layers"
    elif temp < 20: return "Light jacket recommended"
    else: return "T-shirt and light clothing perfect"

def generate_outfit_suggestion(weather, style):
    base = f"For {weather['temperature']}°C {weather['condition']} weather: "
    if style == "casual": return base + "Jeans with comfortable top"
    elif style == "formal": return base + "Tailored pants with button-down"
    else: return base + "Dress for the occasion"

