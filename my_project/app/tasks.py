from celery import Celery
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import requests
from datetime import datetime
from typing import Dict, Any
from config import  AI_SERVER_URL, REDIS_URL
from mbti_calculator import calculate_mbti
from celery.utils.log import get_task_logger
from pathlib import Path
from dotenv import load_dotenv
import os
from supabase import create_client

# Get the path to the .env file in ai_service



# env_path = Path(__file__).parent.parent / 'ai_service' / '.env'
# load_dotenv(env_path)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

logger = get_task_logger(__name__)
print('REDIS_URL:', REDIS_URL)
app = Celery('tasks', broker=REDIS_URL)

@app.task(bind=True, max_retries=3)
def process_ai_task(self, task_id: int):
    try:
        # # 1. 从数据库读取宠物信息
        # conn = psycopg2.connect(**DB_CONFIG)
        # cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 读取宠物信息
        # cur.execute("""
        #     SELECT 
        #         submission_id,
        #         pet_species,
        #         pet_name,
        #         pet_breed,
        #         pet_gender,
        #         pet_age,
        #         personality_behavior
        #     FROM survey_data
        #     WHERE submission_id = %s
        # """, (task_id,))

        pet_data = supabase.table('user_pet_data').select('submission_id, pet_species, pet_name, pet_breed, pet_gender, pet_age, personality_behavior').eq('submission_id', task_id).execute()
        print('pet_data:', pet_data.data[0])
        pet_data = pet_data.data[0]
        if not pet_data:
            raise Exception(f"Pet data not found for task_id: {task_id}")
            
        # 2. 计算MBTI分数
        mbti_scores = calculate_mbti(
            pet_data['personality_behavior'],
            pet_data['pet_species'],
            pet_data['pet_breed']
        )
        print('mbti_scores:', mbti_scores)
        
        # 3. 保存MBTI分数到数据库
        # cur.execute("""
        #     UPDATE survey_data 
        #     SET mbti_scores = %s
        #     WHERE submission_id = %s
        # """, (json.dumps(mbti_scores), task_id))

        supabase.table('user_pet_data').update({'mbti_scores': json.dumps(mbti_scores)}).eq('submission_id', task_id).execute()
        # 4. 准备发送给AI服务的数据
        ai_input = {
            "pet_name": pet_data['pet_name'],
            "pet_gender": pet_data['pet_gender'],
            "pet_age": pet_data['pet_age'],
            "pet_type": pet_data['pet_species'],
            "pet_breed": pet_data['pet_breed'],
            "mbti_scores": {k: round(v) for k, v in mbti_scores.items()}  # 四舍五入为整数
        }
        
        
        
        # 5. 调用AI服务
        # ai_response = requests.post(
        #     f"{AI_SERVER_URL}/ai",
        #     json={"input_data": ai_input},
        #     timeout=200  # 增加超时时间
        # )


    
 

        # url = AI_SERVER_URL.rstrip("/") + "/ai"
        # headers = {"Content-Type": "application/json"}

        # print("Calling AI server at:", url)
        # print("Sending JSON:", {"input_data": ai_input})
   

        # ai_response = requests.post(
        #     url,
        #     headers=headers,
        #     json={"input_data": ai_input},
        #     timeout=200
        # )


        # url = "https://ai-server-production-b3f3.up.railway.app/ai"
        url = AI_SERVER_URL.rstrip("/") + "/ai"
        payload = {
            "input_data": ai_input  # 你原来的数据结构就行
        }
        headers = {
            'Content-Type': 'application/json'
        }

        ai_response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        

        print('ai_response:', ai_response)
        
        if ai_response.status_code != 200:
            raise Exception(f"AI service error: {ai_response.text}")
            
        # ai_result = ai_response.json()
        # print('ai_result:', ai_result.json())

        ai_result = ai_response
    
        
        # 6. 更新数据库中的AI结果
        # cur.execute("""
        #     UPDATE survey_data 
        #     SET ai_output_text = %s,
        #         generated_at = NOW()
        #     WHERE submission_id = %s
        # """, (
        #     json.dumps(ai_result),
        #     task_id
        # ))
       
        # Convert the AI result to a proper JSON string before storing
        update_data = {
            'ai_output_text': json.dumps(ai_result, ensure_ascii=False),  # Convert dict to JSON string
            'generated_at': datetime.now().isoformat(),
        }
        
        result = supabase.table('user_pet_data').update(update_data).eq('submission_id', task_id).execute()
        print(f"Update result: {result}")

        # conn.commit()
        return {"status": "success", "task_id": task_id}
        
    except Exception as e:
        print(f"Error updating record: {str(e)}")
        print(f"Task ID: {task_id}, type: {type(task_id)}")
        print(f"AI Result type: {type(ai_result)}")
        raise
        # 重试任务
        self.retry(exc=e, countdown=20)  # 60秒后重试
        return {"status": "error", "task_id": task_id, "error": str(e)}
   
        # if 'cur' in locals():
        #     cur.close()
        # if 'conn' in locals():
        #     conn.close()