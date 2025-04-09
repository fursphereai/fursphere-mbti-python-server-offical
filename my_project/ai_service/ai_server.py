from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any
import openai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class MbtiOutput(BaseModel):
    m_label: Literal["Extraversion", "Introversion"]
    m_score: int = Field(description="A percentage score between -100 and 100")
    m_explanation: str = Field(description="150-200 characters")

    b_label: Literal["Sensing", "Intuition"]
    b_score: int = Field(description="A percentage score between -100 and 100")
    b_explanation: str = Field(description="150-200 characters")

    t_label: Literal["Thinking", "Feeling"]
    t_score: int = Field(description="A percentage score between -100 and 100")
    t_explanation: str = Field(description="150-200 characters")

    i_label: Literal["Judging", "Perceiving"]
    i_score: int = Field(description="A percentage score between -100 and 100")
    i_explanation: str = Field(description="150-200 characters")

    personal_speech: str = Field(
        description="""
        Something the pet would say to its owner or other people, if it could
        speak, according to its personality. 50-75 characters
        """,
    )

    third_person_diagnosis: str = Field(
        description="""
        A diagnosis of the pet's personality from a third-person perspective. Do
        not include anything already mentioned in the MBTI breakdowns, but
        describe what it might be like to spend time with this pet. 175-216
        characters
        """,
    )

    do_suggestion: str = Field(
        description="""
        Clearly recommend the best ways to positively interact with this pet,
        matching its preferences and comfort. 100-150 characters
        """,
    )

    do_not_suggestion: str = Field(
        description="""
        Humorously and empathetically describe interactions to avoid,
        focusing on the pet's dislikes and sensitivities. 100-150 characters
        """,
    )

class AIInput(BaseModel):
    input_data: Dict[str, Any]

def generate_mbti_description(m_score, b_score, t_score, i_score):
    description = "📊 MBTI Score Interpretation:\n\n"
    
    # E/I Dimension (m_score)
    if m_score >= 60:
        description += "E/I (m_score): Extremely Extraverted - Loves attention, very social, thrives on interaction.\n"
    elif m_score >= 15:
        description += "E/I (m_score): Extraverted - Energetic, playful, enjoys social interaction.\n"
    elif m_score >= -15:
        description += "E/I (m_score): Balanced - Cautious, slightly reserved, but sociable when comfortable.\n"
    elif m_score >= -60:
        description += "E/I (m_score): Introverted - Reserved, calm, and enjoys personal space.\n"
    else:
        description += "E/I (m_score): Extremely Introverted - Highly independent, quiet, and prefers solitude.\n"
    
    # S/N Dimension (b_score)
    if b_score >= 60:
        description += "S/N (b_score): Extremely Sensing - Highly practical, detail-oriented, and reliable.\n"
    elif b_score >= 15:
        description += "S/N (b_score): Sensing - Prefers routine, focuses on tangible details.\n"
    elif b_score >= -15:
        description += "S/N (b_score): Balanced - Combines practical thinking with occasional creativity.\n"
    elif b_score >= -60:
        description += "S/N (b_score): Intuitive - Curious, enjoys exploration and imaginative ideas.\n"
    else:
        description += "S/N (b_score): Highly Intuitive - Visionary, innovative, constantly seeking new possibilities.\n"
    
    # T/F Dimension (t_score)
    if t_score >= 60:
        description += "T/F (t_score): Highly Logical - Independent thinker, prefers strategy and structure.\n"
    elif t_score >= 15:
        description += "T/F (t_score): Logical - Prefers rational decision-making with less emotional influence.\n"
    elif t_score >= -15:
        description += "T/F (t_score): Balanced - Can combine logic and empathy to make decisions.\n"
    elif t_score >= -60:
        description += "T/F (t_score): Feeling - Compassionate, warm, and loyal to loved ones.\n"
    else:
        description += "T/F (t_score): Highly Emotional - Very empathetic, makes decisions based on feelings.\n"
    
    # J/P Dimension (i_score)
    if i_score >= 60:
        description += "J/P (i_score): Extremely Organized - Very structured, reliable, and follows rules strictly.\n"
    elif i_score >= 15:
        description += "J/P (i_score): Organized - Prefers planning and order, but can be flexible if needed.\n"
    elif i_score >= -15:
        description += "J/P (i_score): Balanced - Can adapt between planning and spontaneity as needed.\n"
    elif i_score >= -60:
        description += "J/P (i_score): Perceiving - Prefers flexibility, curious and spontaneous.\n"
    else:
        description += "J/P (i_score): Highly Spontaneous - Loves exploring, very adaptable, enjoys improvisation.\n"
    
    return description

def map_score_to_label(score, dimension):
    if dimension == 'E/I':
        if score > 0:
            return "Extraversion"
        else:
            return "Introversion"
    elif dimension == 'S/N':
        if score > 0:
            return "Sensing"
        else:
            return "Intuition"
    elif dimension == 'T/F':
        if score > 0:
            return "Thinking"
        else:
            return "Feeling"
    elif dimension == 'J/P':
        if score > 0:
            return "Judging"
        else:
            return "Perceiving"

def generate_mbti_do_dont(m_score, b_score, t_score, i_score):
    do_list = []
    dont_list = []

    # E/I Dimension
    if m_score >= 0:
        do_list.append("Provide playful activities and social interaction.")
        dont_list.append("Avoid neglecting their need for attention.")
    else:
        do_list.append("Use calm, gentle interactions; respect their space.")
        dont_list.append("Avoid loud noises or sudden interactions.")

    # S/N Dimension
    if b_score >= 0:
        do_list.append("Keep routines steady and activities familiar.")
        dont_list.append("Avoid frequent changes or too much novelty.")
    else:
        do_list.append("Offer variety and new experiences.")
        dont_list.append("Avoid repetitive or boring tasks.")

    # T/F Dimension
    if t_score >= 0:
        do_list.append("Provide structure and clear guidance.")
        dont_list.append("Avoid emotional or inconsistent responses.")
    else:
        do_list.append("Show warmth and affection consistently.")
        dont_list.append("Avoid being distant or indifferent.")

    # J/P Dimension
    if i_score >= 0:
        do_list.append("Maintain structure and predictable routines.")
        dont_list.append("Avoid chaotic environments or unpredictability.")
    else:
        do_list.append("Encourage creativity and flexible activities.")
        dont_list.append("Avoid strict rules and rigid schedules.")

    # Combine into final strings
    do_final = " ".join(do_list)
    dont_final = " ".join(dont_list)

    return {
        "Do": do_final,
        "Do Not": dont_final
    }

@app.post("/ai", response_model=MbtiOutput)
async def process_ai(input: AIInput):
    try:
        # Get input data
        pet_name = input.input_data["pet_name"]
        pet_gender = input.input_data["pet_gender"]
        pet_age = input.input_data["pet_age"]
        pet_type = input.input_data["pet_type"]
        pet_breed = input.input_data["pet_breed"]
        mbti_scores = input.input_data["mbti_scores"]
        
        # Generate MBTI description
        mbti_description = generate_mbti_description(
            mbti_scores['E/I'],
            mbti_scores['S/N'],
            mbti_scores['T/F'],
            mbti_scores['J/P']
        )
        
        # Generate Do/Don't suggestions
        do_dont_suggestions = generate_mbti_do_dont(
            mbti_scores['E/I'],
            mbti_scores['S/N'],
            mbti_scores['T/F'],
            mbti_scores['J/P']
        )
        
        # Build prompt for AI
        prompt = f"""
        Analyze the personality of {pet_name} ({pet_type}, {pet_gender}, {pet_age} years old, breed: {pet_breed}) based on these MBTI characteristics:
        {mbti_description}
        
        Provide your analysis strictly following this structured format and EXACT character limits:
        [E/I Explanation] (150-200 characters)
        Creatively describe the pet's energy level and social interactions vividly and joyfully, making its character sparkle.

        [S/N Explanation] (150-200 characters)
        Expressively illustrate how the pet perceives the world—through keen senses or playful imagination. Make this description lively.

        [T/F Explanation] (150-200 characters)
        Warmly portray whether this pet is emotionally intuitive or logically grounded, bringing its loving or thoughtful traits alive.

        [J/P Explanation] (150-200 characters)
        Vibrantly depict the pet's style—structured and deliberate or spontaneous and adventurous, highlighting its charming traits.

        [Personal Speech] (50-75 characters)
        Craft a witty, charming, or heartwarming quote that encapsulates the pet's personality.

        [Third Person Diagnosis] (175-216 characters)
        Present an engaging third-person snapshot capturing the pet's personality vividly, filled with charming quirks and endearing qualities.

        [Do] (100-150 characters)
        Based on {do_dont_suggestions['Do']} and pet's age {pet_age}, clearly suggest ideal interactions—playful or gentle activities, preferred communication, and socialization methods.
        
        [Do Not] (100-150 characters)
        Humorously yet empathetically advise to avoid {do_dont_suggestions['Do Not']} andn pet's age {pet_age}, highlighting this pet's dislikes, sensitivities, and situations causing discomfort.
        """
        
        # Call OpenAI API
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a talented, expressive pet psychologist skilled in vivid storytelling.Your goal is to analyze pet personalities with creativity, warmth, and humor. Use engaging, charming, and lively language to vividly illustrate each pet's playful, thoughtful, or unique traits.
                    Descriptions must feel universal, appealing, and delightful, without mentioning breed or animal type.

                    STRICTLY follow these character limits for each section:
                        Explanations: 150-200 characters.
                        Personal Speech (as if the pet speaks): 50-75 characters.
                        Third Person Diagnosis (observer's perspective): 175-216 characters.
                        "Do" Advice: 100-150 characters.
                        "Do Not" Advice: 100-150 characters.
                    
                    Carefully ensure each section precisely meets these requirements.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Get AI's response
        print(completion.choices[0].message.content)
        ai_response = completion.choices[0].message.content
        
        # Parse AI response
        def extract_section(content, section_name):
            start = content.find(f"[{section_name}]")
            if start == -1:
                return ""
            start = content.find("\n", start) + 1
            end = content.find("\n\n", start)
            if end == -1:
                end = len(content)
            return content[start:end].strip()
        
        # Create structured output for frontend
        output = {
            "m_label": map_score_to_label(mbti_scores['E/I'], 'E/I'),
            "m_score": mbti_scores['E/I'],
            "m_explanation": extract_section(ai_response, "E/I Explanation"),
            
            "b_label": map_score_to_label(mbti_scores['S/N'], 'S/N'),
            "b_score": mbti_scores['S/N'],
            "b_explanation": extract_section(ai_response, "S/N Explanation"),
            
            "t_label": map_score_to_label(mbti_scores['T/F'], 'T/F'),
            "t_score": mbti_scores['T/F'],
            "t_explanation": extract_section(ai_response, "T/F Explanation"),
            
            "i_label": map_score_to_label(mbti_scores['J/P'], 'J/P'),
            "i_score": mbti_scores['J/P'],
            "i_explanation": extract_section(ai_response, "J/P Explanation"),
            
            "personal_speech": extract_section(ai_response, "Personal Speech"),
            "third_person_diagnosis": extract_section(ai_response, "Third Person Diagnosis"),
            
            "do_suggestion": extract_section(ai_response, "Do"),
            "do_not_suggestion": extract_section(ai_response, "Do Not")
        }
        
        return MbtiOutput(**output)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
