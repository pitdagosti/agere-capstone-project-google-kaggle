# LANGUAGE ASSESSMENT TOOL FOR CANDIDATES 🌍

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# --- Assessment State Storage ---
ASSESSMENT_STATE_FILE = Path(__file__).parent.parent.parent / "jobs" / "language_assessment_state.json"
ASSESSMENT_STATE_FILE.parent.mkdir(exist_ok=True)


def load_assessment_state() -> Dict:
    """Load assessment state from JSON file"""
    if ASSESSMENT_STATE_FILE.exists():
        try:
            with open(ASSESSMENT_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load assessment state: {e}")
            return {}
    return {}


def save_assessment_state(state: Dict):
    """Save assessment state to JSON file"""
    try:
        with open(ASSESSMENT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save assessment state: {e}")


def increment_failure_count(candidate_id: str, job_id: str) -> int:
    """
    Track failed attempts for a candidate on a specific job.
    Returns the updated failure count.
    """
    state = load_assessment_state()
    
    key = f"{candidate_id}_{job_id}"
    if key not in state:
        state[key] = {
            "failure_count": 0,
            "job_id": job_id,
            "candidate_id": candidate_id,
            "blocked": False,
            "last_attempt": None
        }
    
    state[key]["failure_count"] += 1
    state[key]["last_attempt"] = datetime.now().isoformat()
    
    # Block job after 2 failures
    if state[key]["failure_count"] >= 2:
        state[key]["blocked"] = True
    
    save_assessment_state(state)
    return state[key]["failure_count"]


def is_job_blocked(candidate_id: str, job_id: str) -> bool:
    """Check if a job is blocked for a candidate after 2 failed attempts"""
    state = load_assessment_state()
    key = f"{candidate_id}_{job_id}"
    if key in state:
        return state[key].get("blocked", False)
    return False


def reset_attempts(candidate_id: str, job_id: str):
    """Reset failure count for a new assessment"""
    state = load_assessment_state()
    key = f"{candidate_id}_{job_id}"
    if key in state:
        state[key]["failure_count"] = 0
        state[key]["blocked"] = False
    save_assessment_state(state)


# --- Language Proficiency Levels ---
PROFICIENCY_LEVELS = {
    "beginner": {
        "description": "A1 - Elementary",
        "score": 1,
        "assessment_difficulty": "basic"
    },
    "elementary": {
        "description": "A2 - Elementary",
        "score": 2,
        "assessment_difficulty": "basic"
    },
    "intermediate": {
        "description": "B1 - Intermediate",
        "score": 3,
        "assessment_difficulty": "intermediate"
    },
    "upper_intermediate": {
        "description": "B2 - Upper-Intermediate",
        "score": 4,
        "assessment_difficulty": "intermediate"
    },
    "advanced": {
        "description": "C1 - Advanced",
        "score": 5,
        "assessment_difficulty": "advanced"
    },
    "proficient": {
        "description": "C2 - Mastery",
        "score": 6,
        "assessment_difficulty": "advanced"
    },
    "native": {
        "description": "Native Speaker",
        "score": 7,
        "assessment_difficulty": "advanced"
    }
}

# --- Assessment Templates ---
ASSESSMENT_TEMPLATES = {
    "basic": {
        "comprehension": [
            "Read the following text and answer the questions in {language}:\n\n"
            "'{sample_text}'\n\n"
            "Question: {question}\n"
            "Answer:"
        ],
        "vocabulary": [
            "Complete the sentence using the correct word:\n"
            "'{sentence_with_blank}'\n"
            "Options: {options}\n"
            "Your answer:"
        ],
        "grammar": [
            "Correct the grammar in the following sentence:\n"
            "'{incorrect_sentence}'\n"
            "Your answer:"
        ],
        "writing": [
            "Write a short message (50-100 words) in {language} about:\n"
            "'{topic}'\n"
            "Your response:"
        ]
    },
    "intermediate": {
        "comprehension": [
            "Read the article and summarize the main idea in {language} (100-150 words):\n\n"
            "'{sample_text}'\n\n"
            "Your summary:"
        ],
        "discussion": [
            "Write your opinion on the following topic in {language} (150-200 words):\n"
            "'{topic}'\n"
            "Your response:"
        ],
        "complex_grammar": [
            "Explain the grammatical structure and correct if necessary:\n"
            "'{complex_sentence}'\n"
            "Your analysis:"
        ],
        "business_writing": [
            "Draft a professional email in {language} based on this scenario:\n"
            "'{scenario}'\n"
            "Your email:"
        ]
    },
    "advanced": {
        "comprehension": [
            "Analyze the following passage and provide a critical assessment in {language} (200-300 words):\n\n"
            "'{sample_text}'\n\n"
            "Your analysis:"
        ],
        "debate": [
            "Present a well-argued position on:\n"
            "'{topic}'\n"
            "Include counterarguments and defend your position (300+ words in {language}).\n"
            "Your response:"
        ],
        "technical_communication": [
            "Explain the following technical concept in {language}:\n"
            "'{technical_concept}'\n"
            "Your explanation:"
        ],
        "essay": [
            "Write an essay in {language} on the topic:\n"
            "'{topic}'\n"
            "Requirements:\n"
            "- 400-500 words\n"
            "- Well-structured (introduction, body, conclusion)\n"
            "- Professional tone\n"
            "Your essay:"
        ]
    }
}

# --- Sample Content for Assessments ---
SAMPLE_CONTENT = {
    "basic_texts": {
        "English": "The sun is shining brightly today. I enjoy walking in the park with my friends.",
        "Spanish": "El sol brilla intensamente hoy. Me encanta caminar en el parque con mis amigos.",
        "French": "Le soleil brille intensément aujourd'hui. J'aime marcher dans le parc avec mes amis.",
        "German": "Die Sonne scheint heute hell. Ich gehe gerne im Park mit meinen Freunden spazieren.",
        "Italian": "Il sole splende intensamente oggi. Mi piace passeggiare nel parco con i miei amici."
    },
    "questions": {
        "English": "What is the weather like? Where does the person like to walk?",
        "Spanish": "¿Cómo está el clima? ¿Dónde le gusta caminar a la persona?",
        "French": "Quel temps fait-il? Où la personne aime-t-elle marcher?",
        "German": "Wie ist das Wetter? Wo geht die Person gerne spazieren?",
        "Italian": "Com'è il tempo? Dove piace alla persona camminare?"
    },
    "topics": {
        "intermediate": "Tell me about your experience with technology in the workplace",
        "advanced": "Discuss the impact of artificial intelligence on modern society and the job market"
    }
}


def generate_language_assessment(
    language: str,
    proficiency_level: str,
    candidate_name: str = "Candidate",
    job_title: str = "Unknown Position"
) -> Dict:
    """
    Generate a tailored language assessment for the candidate.

    Args:
        language: The language to assess (e.g., "English", "Spanish")
        proficiency_level: The proficiency level (e.g., "intermediate")
        candidate_name: Name of the candidate
        job_title: Title of the job

    Returns:
        A dictionary containing the assessment details and questions
    """

    if proficiency_level not in PROFICIENCY_LEVELS:
        return {
            "status": "error",
            "message": f"Unknown proficiency level: {proficiency_level}. Supported levels: {list(PROFICIENCY_LEVELS.keys())}"
        }

    level_info = PROFICIENCY_LEVELS[proficiency_level]
    difficulty = level_info["assessment_difficulty"]

    # Determine assessment tasks based on difficulty
    if difficulty == "basic":
        tasks = ["comprehension", "vocabulary", "grammar", "writing"]
    elif difficulty == "intermediate":
        tasks = ["comprehension", "discussion", "complex_grammar", "business_writing"]
    else:  # advanced
        tasks = ["comprehension", "debate", "technical_communication", "essay"]

    assessment_data = {
        "status": "success",
        "candidate_name": candidate_name,
        "job_title": job_title,
        "language": language,
        "proficiency_level": proficiency_level,
        "proficiency_description": level_info["description"],
        "assessment_type": f"{difficulty.upper()} Level Assessment",
        "instructions": f"""
Dear {candidate_name},

This is a {level_info['description']} language proficiency assessment for the position of {job_title}.

Please complete the following tasks in {language}. Your responses will be evaluated on:
- **Vocabulary & Lexis**: Range and accuracy of language use
- **Grammar & Syntax**: Correct use of grammar structures
- **Coherence**: Logical flow and organization
- **Communication**: Clarity and effectiveness of message delivery
- **Task Completion**: Ability to fulfill the requirements

Total estimated time: 20-30 minutes

Begin when ready and submit your complete responses.
        """.strip(),
        "tasks": {}
    }

    # Generate specific tasks
    for i, task_type in enumerate(tasks, 1):
        assessment_data["tasks"][f"Task {i}: {task_type.replace('_', ' ').title()}"] = {
            "type": task_type,
            "question": f"[Assessment Task {i} - {task_type.replace('_', ' ').title()} in {language}]\n\n"
                       f"Please provide your response below:",
            "word_count_guide": "80-120 words" if difficulty == "basic" else
                               "150-250 words" if difficulty == "intermediate" else
                               "300+ words"
        }

    return assessment_data


def evaluate_language_assessment(
    candidate_response: str,
    language: str,
    proficiency_level: str,
    assessment_content: Dict = None
) -> Dict:
    """
    Evaluate the candidate's language assessment response.
    
    This evaluates based on:
    1. Response length and completeness
    2. Language structure and coherence
    3. Vocabulary and grammar indicators
    4. Meeting the task requirements
    
    Args:
        candidate_response: The candidate's written response
        language: The language of assessment
        proficiency_level: Expected proficiency level
        assessment_content: The original assessment (optional, for validation)
    
    Returns:
        A dictionary with evaluation result: "pass" or "not pass"
    """
    
    if not candidate_response or len(candidate_response.strip()) < 10:
        return {
            "result": "not pass",
            "reason": "Response is too short or empty",
            "feedback": "Your response was too brief. Please provide a more detailed answer.",
            "score": 0
        }

    response_length = len(candidate_response.split())
    
    # Define minimum word counts by proficiency
    min_word_counts = {
        "beginner": 20,
        "elementary": 30,
        "intermediate": 80,
        "upper_intermediate": 120,
        "advanced": 200,
        "proficient": 250,
        "native": 100  # Native speakers can be concise
    }
    
    min_words = min_word_counts.get(proficiency_level, 50)
    
    # Basic validation
    if response_length < min_words:
        return {
            "result": "not pass",
            "reason": f"Response too short ({response_length} words, minimum: {min_words})",
            "feedback": f"Your response is too brief. Expected at least {min_words} words, received {response_length}.",
            "score": 20
        }

    # Check for basic coherence indicators
    sentences = [s.strip() for s in candidate_response.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return {
            "result": "not pass",
            "reason": "Response lacks structure (less than 2 sentences)",
            "feedback": "Your response needs better structure. Please write in complete sentences with proper punctuation.",
            "score": 30
        }

    # Evaluate for the language (simple heuristics)
    has_proper_grammar = evaluate_basic_grammar(candidate_response, language)
    has_vocabulary = len(set(candidate_response.split())) > min_words * 0.3  # At least 30% unique words
    
    score = 0
    feedback_parts = []
    
    # Scoring logic based on proficiency
    if proficiency_level in ["beginner", "elementary"]:
        # Basic requirements: length + structure
        if response_length >= min_words and len(sentences) >= 2:
            score = 85
            result = "pass"
            feedback_parts.append("✅ Response meets basic length and structure requirements.")
        else:
            score = 40
            result = "not pass"
            feedback_parts.append("❌ Response does not meet basic requirements.")
    
    elif proficiency_level in ["intermediate", "upper_intermediate"]:
        # Intermediate: length + structure + some vocabulary
        if response_length >= min_words and has_vocabulary and len(sentences) >= 3:
            score = 85
            result = "pass"
            feedback_parts.append("✅ Response demonstrates intermediate proficiency.")
        else:
            score = 45
            result = "not pass"
            feedback_parts.append("❌ Response does not meet intermediate proficiency standards.")
            if response_length < min_words:
                feedback_parts.append(f"  • Too short ({response_length} words)")
            if not has_vocabulary:
                feedback_parts.append(f"  • Limited vocabulary range")
    
    else:  # advanced, proficient, native
        # Advanced: length + structure + grammar + vocabulary + coherence
        if response_length >= min_words and has_vocabulary and has_proper_grammar:
            score = 90
            result = "pass"
            feedback_parts.append("✅ Response demonstrates advanced proficiency.")
        else:
            score = 50
            result = "not pass"
            feedback_parts.append("❌ Response does not meet advanced proficiency standards.")
            if not has_proper_grammar:
                feedback_parts.append(f"  • Grammar issues detected")
            if not has_vocabulary:
                feedback_parts.append(f"  • Limited sophisticated vocabulary")

    feedback = "\n".join(feedback_parts)

    return {
        "result": result,
        "reason": "Assessment evaluation based on response quality and proficiency standards",
        "feedback": feedback,
        "score": score,
        "word_count": response_length,
        "sentence_count": len(sentences),
        "details": {
            "has_proper_grammar": has_proper_grammar,
            "has_vocabulary": has_vocabulary,
            "meets_length": response_length >= min_words
        }
    }


def evaluate_basic_grammar(text: str, language: str) -> bool:
    """
    Simple heuristic to check for basic grammar issues.
    This is NOT a full grammar checker, just basic indicators.
    """
    if not text or len(text) < 10:
        return False
    
    # Basic checks (very simplified)
    # Check for balanced punctuation
    opening_quotes = text.count('"') + text.count("'")
    closing_quotes = text.count('"') + text.count("'")
    
    # Check for proper capitalization in English
    sentences = text.split('.')
    proper_caps = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper() for _ in [1])
    
    # If at least 60% of sentences start with capital, consider decent
    if len(sentences) > 0 and proper_caps / len(sentences) >= 0.6:
        return True
    
    # Alternative: check for common words
    words = text.split()
    if len(words) > 5:
        return True
    
    return False


# Export these as tool functions for the agent
def generate_assessment_for_candidate(
    language: str,
    proficiency_level: str,
    candidate_name: str = "Candidate",
    job_title: str = "Unknown Position"
) -> str:
    """
    Wrapper for agents: Generate a language assessment.
    
    Args:
        language: Language to assess
        proficiency_level: Proficiency level
        candidate_name: Name of candidate
        job_title: Job title candidate is applying for
    
    Returns:
        Formatted string with assessment details
    """
    result = generate_language_assessment(language, proficiency_level, candidate_name, job_title)
    
    if result["status"] == "error":
        return f"❌ Error: {result['message']}"
    
    output = f"""
===== LANGUAGE PROFICIENCY ASSESSMENT =====

Candidate: {result['candidate_name']}
Position: {result['job_title']}
Language: {result['language']}
Level: {result['proficiency_description']}

{result['instructions']}

ASSESSMENT TASKS:
"""
    
    for task_name, task_details in result['tasks'].items():
        output += f"\n{task_name}\n"
        output += f"  Type: {task_details['type'].replace('_', ' ').title()}\n"
        output += f"  Word Count Guide: {task_details['word_count_guide']}\n"
        output += f"  {task_details['question']}\n"
    
    return output


def evaluate_candidate_response(
    candidate_response: str,
    language: str,
    proficiency_level: str,
    candidate_id: str = "unknown",
    job_id: str = "unknown"
) -> str:
    """
    Wrapper for agents: Evaluate candidate's response.
    
    Args:
        candidate_response: The candidate's written response
        language: Language assessed
        proficiency_level: Expected proficiency
        candidate_id: ID of candidate (for tracking)
        job_id: ID of job (for tracking)
    
    Returns:
        "pass" or "not pass" as per requirements
    """
    # Check if job is blocked
    if is_job_blocked(candidate_id, job_id):
        return "not pass"
    
    evaluation = evaluate_language_assessment(candidate_response, language, proficiency_level)
    
    if evaluation["result"] == "pass":
        return "pass"
    else:
        # Increment failure count
        failure_count = increment_failure_count(candidate_id, job_id)
        
        if failure_count >= 2:
            return "not pass"
        
        return "not pass"
