import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rules.outfit_weather import outfit_weather_check
from models import Prediction, Feedback, Base, User, Outfit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_weather_logic():
    print("Testing Weather Logic...")
    
    # Test 1: Comfort
    res = outfit_weather_check("t-shirt", 25, 0, min_temp=20, max_temp=28)
    print(f"Test 1 (Normal): {res}")
    assert "✅" in res, "Should be suitable"

    # Test 2: Extreme Cold
    res = outfit_weather_check("t-shirt", 5, 0, min_temp=2, max_temp=10)
    print(f"Test 2 (Cold): {res}")
    assert "❌" in res and "Extreme cold" in res, "Should warn about cold"

    # Test 3: Daily High Heat warning even if current temp is ok
    res = outfit_weather_check("jacket", 25, 0, min_temp=20, max_temp=38)
    print(f"Test 3 (Future Heat): {res}")
    assert "❌" in res and "Extreme heat" in res, "Should warn about daily high"
    
    # Test 4: Rain
    res = outfit_weather_check("suede shoes", 20, 0, min_temp=18, max_temp=22, rain_prob=60)
    print(f"Test 4 (Rain Prob): {res}")
    assert "❌" in res and "Rain expected" in res, "Should warn about rain"

    print("Weather Logic Tests Passed! ✅")

def test_db_models():
    print("\nTesting Database Models...")
    
    # Use in-memory SQLite
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Create User
    user = User(email="test@example.com", password="hashed_pw")
    session.add(user)
    session.commit()
    
    # 2. Create Prediction
    pred = Prediction(
        user_id=user.id, 
        image_url="http://img.com", 
        predicted_category="shirt",
        confidence=0.9
    )
    session.add(pred)
    session.commit()
    
    # 3. Create Feedback linked to Prediction
    fb = Feedback(
        prediction_id=pred.id,
        user_label="t-shirt",
        is_helpful=1
    )
    session.add(fb)
    session.commit()
    
    # Verify relations
    fetched_pred = session.query(Prediction).first()
    assert fetched_pred.feedback.user_label == "t-shirt"
    
    print("Database Model Tests Passed! ✅")

if __name__ == "__main__":
    try:
        test_weather_logic()
        test_db_models()
        print("\nAll System Checks Passed Successfully! 🚀")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
