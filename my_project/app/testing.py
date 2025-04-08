from dotenv import load_dotenv
import os
from supabase import create_client
import json
from datetime import datetime
from pathlib import Path
# Load environment variables
# Get the path to the .env file in ai_service
env_path = Path(__file__).parent.parent / 'ai_service' / '.env'
load_dotenv(env_path)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

print(supabase_url)
print(supabase_key)
supabase = create_client(supabase_url, supabase_key)




def submit_survey():
    try:
  
        
        # Prepare data for Supabase
        test_data = [
            {
            'name': 'Test User 1',
            'email': 'test1@example.com',
            'ip': '192.168.1.1',
            'mbti': 'INFJ',
            'test_times': '1',
            'test_date': '2024-01-20',
            'signup': True,
            'email_signup_time': '2024-01-20T10:00:00',
            'pet_name': 'Max',
            'pet_species': 'Dog',
            'pet_breed': 'Golden Retriever',
            'pet_breedcustom': '',
            'pet_gender': 'Male',
            'pet_age': '3',
            'pet_photo': 'https://baywrgbxvrfhttfhwggf.supabase.co/storage/v1/object/public/pet-photos/test1.jpg',
            'personality_behavior': {
                'friendly': 5,
                'active': 4,
                'intelligent': 5,
                'protective': 3
            }
        }
        ]
        
        # Insert into Supabase
        # result = supabase.table('user_pet_data').insert(test_data).execute()

        result = supabase.table('user_pet_data').select('*').eq('submission_id', '4').execute()
        print('result:', result.data[0]['submission_id'])





    # try:
    #     supabase = create_client(
    #         os.getenv('SUPABASE_URL'),
    #         os.getenv('SUPABASE_KEY')
    #     )
    
    # # Test the connection
    #     test_query = supabase.table('user_pet_data').select('*').limit(1).execute()
    #     print("Connection test:", test_query)
    
    # except Exception as e:
    #     print("Supabase initialization error:", str(e))
        
        # Get the submission_id from the response
        
    
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
    

submit_survey()