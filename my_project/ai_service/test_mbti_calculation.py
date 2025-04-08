import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.mbti_calculator import calculate_mbti
import requests
import json
from dotenv import load_dotenv

def print_ai_analysis(result, mbti_scores):
    print("\nMBTI Analysis Results:")
    print("-" * 50)
    
    # Round scores for display
    rounded_scores = {k: round(v) for k, v in mbti_scores.items()}
    
    print("\nOriginal MBTI Scores (-100 to 100):")
    print(json.dumps(rounded_scores, indent=2, ensure_ascii=False))
    
    # Calculate deviation scores using rounded scores
    deviation_scores = {
        "E/I": convert_to_deviation_score(rounded_scores["E/I"], "E/I"),
        "S/N": convert_to_deviation_score(rounded_scores["S/N"], "S/N"),
        "T/F": convert_to_deviation_score(rounded_scores["T/F"], "T/F"),
        "J/P": convert_to_deviation_score(rounded_scores["J/P"], "J/P")
    }
    
    print("\nMBTI Deviation Scores (0-100, 0=balanced, 100=extreme):")
    print(json.dumps(deviation_scores, indent=2, ensure_ascii=False))
    
    # Define dimension labels
    dimensions = {
        "E/I": ("Introversion", "Extraversion"),  # 负值表示内向，正值表示外向
        "S/N": ("Intuition", "Sensing"),         # 负值表示直觉，正值表示感知
        "T/F": ("Feeling", "Thinking"),          # 负值表示感性，正值表示理性
        "J/P": ("Perceiving", "Judging")         # 负值表示知觉，正值表示判断
    }
    
    # Map AI result keys to dimension keys
    dimension_map = {
        'm_score': 'E/I',
        'b_score': 'S/N',
        't_score': 'T/F',
        'i_score': 'J/P'
    }
    
    # Print MBTI dimensions with correct labels
    for dim, (low, high) in dimensions.items():
        score = rounded_scores[dim]
        dev_score = deviation_scores[dim]
        label = high if score > 0 else low  # 修改判断条件
        
        print(f"\n{dim} Dimension:")
        print(f"Original Score: {score} ({label})")
        print(f"Deviation Score: {dev_score}")
        
        # Map dimension to AI result key for explanation
        for ai_key, mapped_dim in dimension_map.items():
            if mapped_dim == dim:
                exp_key = ai_key.replace('score', 'explanation')
                print(f"Explanation: {result[exp_key]}")
                break
    
    print("\n" + "-" * 50)
    print("Personalized Quote:")
    print(result['personal_speech'])
    
    print("\n" + "-" * 50)
    print("Third Person Diagnosis:")
    print(result['third_person_diagnosis'])
    
    print("\n" + "-" * 50)
    print("Interaction Guidelines:")
    print("Recommended Interactions:")
    print(result['do_suggestion'])
    print("\nInteractions to Avoid:")
    print(result['do_not_suggestion'])
    print("-" * 50)
    
    # Print personality tendency analysis
    print("\nPersonality Tendency Analysis:")
    print("-" * 50)
    
    for dim, (low, high) in dimensions.items():
        score = deviation_scores[dim]
        if score < 20:
            strength = "Very Balanced"
        elif score < 40:
            strength = "Moderately Balanced"
        elif score < 60:
            strength = "Slight Tendency"
        elif score < 80:
            strength = "Strong Tendency"
        else:
            strength = "Extreme Tendency"
        
        label = high if rounded_scores[dim] > 0 else low  # 修改判断条件
        print(f"{dim}: {score} - {strength} ({label})")

def process_survey_data(survey_data):
    # 提取宠物信息
    pet_info = survey_data["pet_info"]
    personality_data = survey_data["personality_and_behavior"]
    
    # 直接使用原始数据，让 mbti_calculator 处理数据清理
    personality_behavior = {
        "Energy_Socialization": {
            "seek_attention": personality_data["Energy_Socialization"]["seek_attention"],
            "friend_visit_behaviors": personality_data["Energy_Socialization"]["friend_visit_behaviors"],
            "react_new_friend": personality_data["Energy_Socialization"]["react_new_friend"]
        },
        "Routin_Curiosity": {
            "interact_with_toys": personality_data["Routin_Curiosity"]["interact_with_toys"],
            "fur_care_7days": personality_data["Routin_Curiosity"]["fur_care_7days"],
            "react_new_environment": personality_data["Routin_Curiosity"]["react_new_environment"]
        },
        "Decision_Making": {
            "stranger_enter_territory": personality_data["Decision_Making"]["stranger_enter_territory"],
            "react_when_sad": personality_data["Decision_Making"]["react_when_sad"],
            "respond_to_scold": personality_data["Decision_Making"]["respond_to_scold"]
        },
        "Structure_Spontaneity": {
            "prefer_routine": personality_data["Structure_Spontaneity"]["prefer_routine"],
            "toy_out_of_reach": personality_data["Structure_Spontaneity"]["toy_out_of_reach"],
            "follow_commands": personality_data["Structure_Spontaneity"]["follow_commands"]
        }
    }
    
    return {
        "personality_behavior": personality_behavior,
        "pet_type": pet_info["PetSpecies"],
        "pet_breed": pet_info["PetBreed"],
        "pet_name": pet_info["PetName"],
        "pet_gender": pet_info["PetGender"],
        "pet_age": pet_info["PetAge"]
    }

def convert_to_deviation_score(score, label):
    """
    将-100到100的分数转换为偏差值（0表示平衡，100表示极端）
    """
    return abs(score/2) + 50 # 直接使用绝对值作为偏差值

def test_mbti():
    while True:
        print("\nMBTI Test Menu:")
        print("1. Start new test")
        print("2. Exit")
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "2":
            print("Exiting program. Goodbye!")
            break
        elif choice != "1":
            print("Invalid choice. Please try again.")
            continue
            
        print("\nPaste your JSON data (press Enter twice to finish):")
        json_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            json_lines.append(line)
        
        try:
            json_str = "\n".join(json_lines)
            data = json.loads(json_str)
            
            # Process data
            test_data = process_survey_data(data["surveyData"])
            
            print("\nProcessed test data:")
            print(json.dumps(test_data, indent=2, ensure_ascii=False))
            
            print("\nCalculating MBTI scores...")
            # 使用 mbti_calculator 中的函数计算分数
            mbti_scores = calculate_mbti(
                test_data["personality_behavior"],
                test_data["pet_type"],
                test_data["pet_breed"]
            )
            
            print("\nCalculated MBTI scores:")
            print(json.dumps(mbti_scores, indent=2, ensure_ascii=False))
            
            # 为AI服务准备整数分数
            ai_input = {
                "input_data": {
                    "pet_name": test_data["pet_name"],
                    "pet_type": test_data["pet_type"],
                    "pet_breed": test_data["pet_breed"],
                    "pet_gender": test_data["pet_gender"],
                    "pet_age": test_data["pet_age"],
                    "mbti_scores": {k: round(v) for k, v in mbti_scores.items()}  # 四舍五入为整数
                }
            }
            
            try:
                # Send to AI service
                response = requests.post("http://localhost:8001/ai", json=ai_input)
                
                if response.status_code == 200:
                    ai_result = response.json()
                    print_ai_analysis(ai_result, mbti_scores)
                else:
                    print(f"Error: AI service returned status code {response.status_code}")
                    print(response.text)
            except requests.exceptions.ConnectionError:
                print("Error: Could not connect to AI service. Please ensure the AI server is running.")
                break
        except json.JSONDecodeError:
            print("Error: Invalid JSON data format")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\nPress Enter to continue...")
        input()

if __name__ == "__main__":
    load_dotenv()
    test_mbti()