from flask import Flask, request, jsonify
import json
import psycopg2
# from config import DB_CONFIG
from tasks import process_ai_task
from pathlib import Path
from dotenv import load_dotenv
import os
from supabase import create_client
import json
from datetime import datetime

# Get the path to the .env file in ai_service
env_path = Path(__file__).parent.parent / 'ai_service' / '.env'
load_dotenv(env_path)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

app = Flask(__name__)

# def connect_db():
#     return psycopg2.connect(**DB_CONFIG)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        if not data or not data['survey_data']:
            return jsonify({"error": "Invalid data format"}), 400

        survey_data = data["survey_data"]
        print('survey_data:', survey_data)
       
        # conn = connect_db()
        # cursor = conn.cursor()

        # 1. Flask API Stores Data in PostgreSQL


        print("Values to insert:", (
            survey_data["user_info"].get("name", ""),
            survey_data["user_info"].get("email", ""), 
            survey_data["user_info"].get("ip", ""),
            survey_data["user_info"].get("mbti", ""),
            survey_data["user_info"].get("test_times", ""),
            survey_data["user_info"].get("test_date", ""),
            survey_data["user_info"].get("signup", ""),
            survey_data["user_info"].get("email_signup_time", ""),
            survey_data["pet_info"].get("PetName", ""),
            survey_data["pet_info"].get("PetSpecies", ""),
            survey_data["pet_info"].get("PetBreed", ""),
            survey_data["pet_info"].get("PetBreedCustom", ""),
            survey_data["pet_info"].get("PetGender", ""),
            survey_data["pet_info"].get("PetAge", ""),
            survey_data["pet_info"].get("PetPhoto", ""),
            json.dumps(survey_data.get("personality_and_behavior", {}))
  
))      
        
        insert_data = [
            {
            'name':  survey_data["user_info"].get("name", ""),
            'email': survey_data["user_info"].get("email", ""), 
            'ip': survey_data["user_info"].get("ip", ""),
            'mbti':  survey_data["user_info"].get("mbti", ""),
            'test_times': survey_data["user_info"].get("test_times", ""),
            'test_date': survey_data["user_info"].get("test_date", ""),
            'signup': survey_data["user_info"].get("signup", ""),
            'email_signup_time': survey_data["user_info"].get("email_signup_time", ""),
            'pet_name':  survey_data["pet_info"].get("PetName", ""),
            'pet_species':survey_data["pet_info"].get("PetSpecies", ""),
            'pet_breed': survey_data["pet_info"].get("PetBreed", ""),
            'pet_breedcustom': survey_data["pet_info"].get("PetBreedCustom", ""),
            'pet_gender': survey_data["pet_info"].get("PetGender", ""),
            'pet_age': survey_data["pet_info"].get("PetAge", ""),
            'pet_photo': survey_data["pet_info"].get("PetPhoto", ""),
            'personality_behavior': survey_data.get("personality_and_behavior", {})
            #    json.dumps(survey_data.get("personality_and_behavior", {}))

            
            }
        ]



        result = supabase.table('user_pet_data').insert(insert_data).execute()

        


        # cursor.execute("""
        #     INSERT INTO survey_data (
        #         name, email, ip, mbti, test_times, test_date, signup, email_signup_time,
        #         pet_name, pet_species, pet_breed, pet_breedcustom, pet_gender, pet_age, pet_photo,
        #         personality_behavior
        #     )
        #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        #     RETURNING submission_id;
        # """, (
        #     survey_data["user_info"].get("name", ""),
        #     survey_data["user_info"].get("email", ""), 
        #     survey_data["user_info"].get("ip", ""),
        #     survey_data["user_info"].get("mbti", ""),
        #     survey_data["user_info"].get("test_times", ""),
        #     survey_data["user_info"].get("test_date", ""),
        #     survey_data["user_info"].get("signup", ""),
        #     survey_data["user_info"].get("email_signup_time", ""),
        #     survey_data["pet_info"].get("PetName", ""),
        #     survey_data["pet_info"].get("PetSpecies", ""),
        #     survey_data["pet_info"].get("PetBreed", ""),
        #     survey_data["pet_info"].get("PetBreedCustom", ""),
        #     survey_data["pet_info"].get("PetGender", ""),
        #     survey_data["pet_info"].get("PetAge", ""),
        #     survey_data["pet_info"].get("PetPhoto", ""),
        #     json.dumps(survey_data.get("personality_and_behavior", {}))
        # ))

        submission_id = result.data[0]['submission_id']
        print('submission_id:', submission_id)
        # conn.commit()
        # cursor.close()
        # conn.close()

        # 2. Flask Queues Task for Celery to Process AI
        process_ai_task.delay(submission_id)

  
        return jsonify({
            'status': 'processing',
            'submission_id': submission_id,
            'message': 'Your survey has been submitted and is being processed.',
            'timestamp': datetime.now().isoformat(),
        }), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_result/<int:submission_id>', methods=['GET'])
def get_result(submission_id):
   
    print('submission_idfor getting:', submission_id)

  
    result = supabase.table('user_pet_data').select('ai_output_text, generated_at, name, email, ip, mbti, test_times, test_date, signup, email_signup_time, pet_name, pet_species, pet_breed, pet_breedcustom, pet_gender, pet_age, pet_photo').eq('submission_id', submission_id).execute()
    result = result.data[0]
    
    if not result['ai_output_text']:
        return jsonify({"status": "processing"}), 202

    # Parse the JSON string back into a dictionary
    ai_output = json.loads(result['ai_output_text']) if isinstance(result['ai_output_text'], str) else result['ai_output_text']

    return jsonify({
        "status": "completed", 
        "ai_output": {
            "text": ai_output,  # Use the parsed JSON
            "generated_at": result['generated_at'] if result['generated_at'] else None
        },
        "user_info": {
            "name": result['name'],
            "email": result['email'],
            "ip": result['ip'],
            "mbti": result['mbti'],
            "test_times": result['test_times'],
            "test_date": result['test_date'],
            "signup": result['signup'],
            "email_signup_time": result['email_signup_time'],
        },
        "pet_info": {
            "pet_name": result['pet_name'],
            "pet_species": result['pet_species'],
            "pet_breed": result['pet_breed'],
            "pet_breedcustom": result['pet_breedcustom'],
            "pet_gender": result['pet_gender'],
            "pet_age": result['pet_age'],
            "pet_photo": result['pet_photo'],
        }
    })

@app.route('/get_user_info/<string:email>', methods=['GET'])
def get_user_info(email):
    print('emailfor getting:', email)

  
    result = supabase.table('user_pet_data').select('ai_output_text, generated_at, name, email, ip, mbti, test_times, test_date, signup, email_signup_time, pet_name, pet_species, pet_breed, pet_breedcustom, pet_gender, pet_age, pet_photo').eq('email', email).execute()
    result = result.data[0]
    
    if not result['ai_output_text']:
        return jsonify({"status": "processing"}), 202

    # Parse the JSON string back into a dictionary
    ai_output = json.loads(result['ai_output_text']) if isinstance(result['ai_output_text'], str) else result['ai_output_text']

    return jsonify({
        "status": "completed", 
        "ai_output": {
            "text": ai_output,  # Use the parsed JSON
            "generated_at": result['generated_at'] if result['generated_at'] else None
        },
        "user_info": {
            "name": result['name'],
            "email": result['email'],
            "ip": result['ip'],
            "mbti": result['mbti'],
            "test_times": result['test_times'],
            "test_date": result['test_date'],
            "signup": result['signup'],
            "email_signup_time": result['email_signup_time'],
        },
        "pet_info": {
            "pet_name": result['pet_name'],
            "pet_species": result['pet_species'],
            "pet_breed": result['pet_breed'],
            "pet_breedcustom": result['pet_breedcustom'],
            "pet_gender": result['pet_gender'],
            "pet_age": result['pet_age'],
            "pet_photo": result['pet_photo'],
        }
    })

@app.route('/check_signup', methods=['GET'])
def check_signup():
    try:
      
        email = request.args.get('email')
        print(f'Email from query: {email}')
        
        result = supabase.table('user_pet_data')\
            .select('signup')\
            .eq('email', email)\
            .execute()
        print('result:', result.data)
        print('len(result.data):', len(result.data))
            
        if len(result.data) == 0:
            return jsonify({
                "status": "completed",  # Changed from 'error' to 'completed'
                "signup": False  # Email doesn't exist, so not signed up
            })
    
        return jsonify({
            "status": "completed", 
            "signup": result.data[0].get('signup')
        })
            
            
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)


    


