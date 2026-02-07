from rules.outfit_weather import outfit_weather_check

def test_verdict():
    # User scenario
    outfit = "blouse"
    current_temp = 30.85
    min_temp = 18.03
    max_temp = 32.12
    rain_prob = 0
    
    print(f"Testing Scenario: Outfit={outfit}, Cur={current_temp}, Min={min_temp}, Max={max_temp}")
    
    verdict = outfit_weather_check(
        outfit, 
        current_temp, 
        0, 
        min_temp=min_temp, 
        max_temp=max_temp, 
        rain_prob=rain_prob
    )
    
    print(f"Verdict: {verdict}")

if __name__ == "__main__":
    test_verdict()
