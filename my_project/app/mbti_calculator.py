from typing import Dict, Any
import pandas as pd
import os
import random  # 需要添加这个导入

# 读取狗的MBTI分数数据
def load_dog_mbti_scores():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dog_raw_mbti_scores.csv')
    return pd.read_csv(csv_path)

# 获取狗的品种MBTI分数
def get_dog_breed_scores(breed: str) -> Dict[str, float]:
    df = load_dog_mbti_scores()
    breed_data = df[df['breed'] == breed].iloc[0] if not df[df['breed'] == breed].empty else None


    if breed_data is None:
        return None
        
    return {
        "E/I": breed_data['m_score'],
        "S/N": breed_data['b_score'],
        "T/F": breed_data['t_score'],
        "J/P": breed_data['i_score']
    }

def calculate_behavior_scores(personality_behavior: Dict[str, Any]) -> Dict[str, float]:
    # 计算原始分数，范围是-100到100
    result = {}

    def safe_float(value: Any) -> float:
        if value is None or value == '':
            return 0
        if isinstance(value, (int, float)):
            return float(value)  # 直接返回数值
        if isinstance(value, str):
            # 移除所有不可见字符和括号
            value = ''.join(char for char in value if char.isprintable())
            value = value.strip(')')
            try:
                return float(value)
            except ValueError:
                return 0
        return 0

    def calculate_dimension(scores: list) -> float:
        # 过滤掉无效值（None, '', 非数字字符串）
        valid_scores = [score for score in scores if isinstance(score, (int, float)) and -100 <= score <= 100]
        if not valid_scores:
            return 0  # 如果没有有效分数，返回中性值
        return sum(valid_scores) / len(valid_scores)  # 直接使用原始分数

    # Energy & Socialization (E vs. I)
    e_vs_i_scores = [
        safe_float(personality_behavior["Energy_Socialization"]["seek_attention"]),
        safe_float(personality_behavior["Energy_Socialization"]["friend_visit_behaviors"]),
        safe_float(personality_behavior["Energy_Socialization"]["react_new_friend"])
    ]
    result["E/I"] = calculate_dimension(e_vs_i_scores)

    # Routine vs. Curiosity (S vs. N)
    s_vs_n_scores = [
        safe_float(personality_behavior["Routin_Curiosity"]["interact_with_toys"]),
        safe_float(personality_behavior["Routin_Curiosity"]["fur_care_7days"]),
        safe_float(personality_behavior["Routin_Curiosity"]["react_new_environment"])
    ]
    result["S/N"] = calculate_dimension(s_vs_n_scores)

    # Decision-Making (T vs. F)
    t_vs_f_scores = [
        safe_float(personality_behavior["Decision_Making"]["stranger_enter_territory"]),
        safe_float(personality_behavior["Decision_Making"]["react_when_sad"]),
        safe_float(personality_behavior["Decision_Making"]["respond_to_scold"])
    ]
    result["T/F"] = calculate_dimension(t_vs_f_scores)

    # Structure vs. Spontaneity (J vs. P)
    j_vs_p_scores = [
        safe_float(personality_behavior["Structure_Spontaneity"]["prefer_routine"]),
        safe_float(personality_behavior["Structure_Spontaneity"]["toy_out_of_reach"]),
        safe_float(personality_behavior["Structure_Spontaneity"]["follow_commands"])
    ]
    result["J/P"] = calculate_dimension(j_vs_p_scores)

    return result

def calculate_mbti(personality_behavior: Dict[str, Any], pet_type: str = None, pet_breed: str = None) -> Dict[str, float]:
    # 计算行为数据分数
    behavior_scores = calculate_behavior_scores(personality_behavior)
    
    # 处理0分情况，随机加减14以内的数字
    for dimension in behavior_scores:
        if behavior_scores[dimension] == 0:
            # 生成-14到14之间的随机数
            random_adjustment = random.randint(-14, 14)
            behavior_scores[dimension] = random_adjustment
    
    # 如果是狗且有品种信息，结合品种预设分数
    #if pet_type == "Dog" and pet_breed:
        #breed_scores = get_dog_breed_scores(pet_breed)
        #if breed_scores:
            #result = {}
            #for dimension in ["E/I", "S/N", "T/F", "J/P"]:
                #breed_score = breed_scores[dimension]
                #behavior_score = behavior_scores[dimension]
                #result[dimension] = breed_score * 0.2 + behavior_score * 0.8
            #return result
    
    # 如果不是狗或没有品种信息，只使用行为数据
    return behavior_scores 