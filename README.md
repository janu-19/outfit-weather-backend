# Outfit Weather Prediction Backend

AI-powered outfit recommendation system based on weather conditions.

## Features

-  **Image-based Outfit Recognition**: Upload an image to identify the type of outfit
-  **Weather Integration**: Get weather data for any city using OpenWeatherMap API
-  **Smart Recommendations**: Receive outfit suggestions based on temperature and weather conditions
-  **Travel Packing**: Get packing recommendations for your travel destination
-  **Accessories Suggestions**: Get accessory recommendations based on outfit and weather
-  **Material Analysis**: Analyze if the material of your outfit is suitable for the weather

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **PIL/Pillow** - Image processing and feature extraction
- **scikit-learn** - Machine learning for outfit classification
- **OpenWeatherMap API** - Weather data
- **SQLAlchemy** - Database ORM
- **Cloudinary** - Image storage
- **Python 3.10+**

## Setup

1. Clone the repository:
```bash
git clone https://github.com/janu-19/outfit-weather-backend.git
cd outfit-weather-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
OPENWEATHER_API_KEY=your_api_key_here
```

Get your API key from [OpenWeatherMap](https://openweathermap.org/api)

4. Run the server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `POST /predict-outfit` - Predict outfit type from image
- `POST /outfit-weather` - Get outfit recommendations based on weather
- `GET /travel-pack?city={city_name}` - Get travel packing recommendations

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT

