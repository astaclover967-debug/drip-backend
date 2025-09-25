from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS for mobile app - CORRECTED VERSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],  # FIXED: was allow_allow_headers
)

@app.get("/")
async def root():
    return {"message": "Drip AI Backend is LIVE!", "status": "success"}

@app.get("/test-connection")
async def test_connection():
    return JSONResponse({
        "status": "success", 
        "message": "Backend is fully operational!",
        "version": "1.0.0"
    })

@app.post("/virtual-try-on")
async def virtual_try_on(user_image: UploadFile = File(...), clothing_image: UploadFile = File(...)):
    """
    SIMPLIFIED VERSION - Basic image receipt confirmation
    """
    try:
        # Simply confirm we received the images
        user_data = await user_image.read()
        clothing_data = await clothing_image.read()
        
        return JSONResponse({
            "success": True,
            "message": "Images received successfully! Virtual try-on processing available in full version.",
            "user_image_size": len(user_data),
            "clothing_image_size": len(clothing_data),
            "status": "demo_mode_ready"
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Processing error: {str(e)}"}, status_code=500)

@app.get("/analyze-weather")
async def analyze_weather(lat: float, lon: float):
    """
    Mock weather data for testing
    """
    return JSONResponse({
        "temperature": 22.5,
        "condition": "Clear",
        "recommendation": "Perfect weather for light clothing",
        "city": "Demo City"
    })

@app.post("/suggest-outfit")
async def suggest_outfit(weather_data: dict, style: str = "casual"):
    """
    Basic outfit suggestion logic
    """
    temp = weather_data.get('temperature', 20)
    condition = weather_data.get('condition', 'Clear')
    
    if temp < 10:
        base = "Cold weather: Wear heavy jacket and layers"
    elif temp < 20:
        base = "Cool weather: Light jacket recommended"
    else:
        base = "Warm weather: T-shirt and light clothing perfect"
    
    suggestion = f"{base} - Style: {style} - Condition: {condition}"
    
    return JSONResponse({
        "suggestion": suggestion,
        "confidence": "85%",
        "weather_considered": True
    })
