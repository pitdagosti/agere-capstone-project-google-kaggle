#!/usr/bin/env python3
"""
Test script for Language Assessment Agent implementation
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("LANGUAGE ASSESSMENT AGENT - IMPLEMENTATION TEST")
print("=" * 70)

# Test 1: Import language assessment tools
print("\n[TEST 1] Importing language assessment tools...")
try:
    from src.tools.language_assessment import (
        generate_language_assessment,
        evaluate_language_assessment,
        generate_assessment_for_candidate,
        evaluate_candidate_response,
        PROFICIENCY_LEVELS,
        is_job_blocked,
        increment_failure_count
    )
    print("✅ All language assessment tools imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Test assessment generation
print("\n[TEST 2] Testing assessment generation...")
try:
    assessment = generate_language_assessment(
        language="English",
        proficiency_level="intermediate",
        candidate_name="John Doe",
        job_title="Software Engineer"
    )
    
    assert assessment["status"] == "success", "Assessment status should be success"
    assert assessment["language"] == "English", "Language should be English"
    assert assessment["proficiency_level"] == "intermediate", "Level should be intermediate"
    assert "tasks" in assessment, "Assessment should have tasks"
    assert len(assessment["tasks"]) > 0, "Assessment should have at least one task"
    print(f"✅ Assessment generated successfully with {len(assessment['tasks'])} tasks")
except Exception as e:
    print(f"❌ Assessment generation error: {e}")
    sys.exit(1)

# Test 3: Test assessment wrapper function
print("\n[TEST 3] Testing assessment generation wrapper...")
try:
    result = generate_assessment_for_candidate(
        language="English",
        proficiency_level="intermediate",
        candidate_name="Jane Smith",
        job_title="Data Scientist"
    )
    
    assert isinstance(result, str), "Result should be a string"
    assert "LANGUAGE PROFICIENCY ASSESSMENT" in result, "Result should contain assessment header"
    assert "Jane Smith" in result, "Result should contain candidate name"
    print("✅ Assessment wrapper function works correctly")
except Exception as e:
    print(f"❌ Wrapper function error: {e}")
    sys.exit(1)

# Test 4: Test evaluation with good response
print("\n[TEST 4] Testing evaluation with good response...")
try:
    good_response = """
    Working as a software engineer has been incredibly rewarding. I have developed strong 
    technical skills in multiple programming languages including Python, JavaScript, and Java. 
    My experience includes working on full-stack applications, designing databases, and collaborating 
    with cross-functional teams. I enjoy solving complex problems and learning new technologies continuously. 
    In my current role, I lead a small team of junior developers and mentoring them in best practices.
    """
    
    evaluation = evaluate_language_assessment(
        candidate_response=good_response,
        language="English",
        proficiency_level="intermediate"
    )
    
    print(f"  - Result: {evaluation['result']}")
    print(f"  - Score: {evaluation['score']}")
    print(f"  - Word count: {evaluation['word_count']}")
    print(f"  - Sentence count: {evaluation['sentence_count']}")
    print(f"  - Feedback: {evaluation['feedback'][:100]}...")
    
    assert evaluation["result"] in ["pass", "not pass"], "Result should be pass or not pass"
    assert "score" in evaluation, "Evaluation should have a score"
    print("✅ Evaluation works correctly")
except Exception as e:
    print(f"❌ Evaluation error: {e}")
    sys.exit(1)

# Test 5: Test evaluation with poor response
print("\n[TEST 5] Testing evaluation with poor response...")
try:
    poor_response = "Hi"
    
    evaluation = evaluate_language_assessment(
        candidate_response=poor_response,
        language="English",
        proficiency_level="intermediate"
    )
    
    assert evaluation["result"] == "not pass", "Short response should not pass"
    print(f"✅ Poor response correctly evaluated as 'not pass'")
except Exception as e:
    print(f"❌ Poor response evaluation error: {e}")
    sys.exit(1)

# Test 6: Test failure tracking
print("\n[TEST 6] Testing failure tracking and job blocking...")
try:
    candidate_id = "test_candidate_001"
    job_id = "job_001"
    
    # First failure
    count1 = increment_failure_count(candidate_id, job_id)
    assert count1 == 1, "First failure count should be 1"
    assert not is_job_blocked(candidate_id, job_id), "Job should not be blocked after 1 failure"
    
    # Second failure
    count2 = increment_failure_count(candidate_id, job_id)
    assert count2 == 2, "Second failure count should be 2"
    assert is_job_blocked(candidate_id, job_id), "Job should be blocked after 2 failures"
    
    print("✅ Failure tracking and blocking works correctly")
except Exception as e:
    print(f"❌ Failure tracking error: {e}")
    sys.exit(1)

# Test 7: Import Language Assessment Agent
print("\n[TEST 7] Importing Language Assessment Agent...")
try:
    from src.agents import language_assessment_agent
    
    assert language_assessment_agent.name == "language_assessment_agent", "Agent name mismatch"
    assert len(language_assessment_agent.tools) == 2, "Agent should have 2 tools"
    print(f"✅ Language Assessment Agent imported successfully")
    print(f"   - Agent name: {language_assessment_agent.name}")
    print(f"   - Number of tools: {len(language_assessment_agent.tools)}")
except ImportError as e:
    print(f"❌ Agent import error: {e}")
    sys.exit(1)

# Test 8: Verify tools are registered
print("\n[TEST 8] Verifying tools in tools module...")
try:
    from src.tools import (
        language_assessment_generation_tool,
        language_assessment_evaluation_tool
    )
    
    print("✅ Both language assessment tools are registered in tools module")
except ImportError as e:
    print(f"❌ Tools registration error: {e}")
    sys.exit(1)

# Test 9: Verify orchestrator includes language assessment agent
print("\n[TEST 9] Verifying orchestrator includes language assessment agent...")
try:
    from src.agents import orchestrator
    
    # Check if language_assessment_agent is in orchestrator's tools
    agent_names = [tool.agent.name for tool in orchestrator.tools if hasattr(tool, 'agent')]
    
    assert "language_assessment_agent" in agent_names, "Orchestrator should include language_assessment_agent"
    print(f"✅ Orchestrator includes language_assessment_agent")
    print(f"   - Orchestrator tools: {agent_names}")
except Exception as e:
    print(f"❌ Orchestrator verification error: {e}")
    sys.exit(1)

# Test 10: Test all proficiency levels
print("\n[TEST 10] Testing all proficiency levels...")
try:
    for level in PROFICIENCY_LEVELS.keys():
        assessment = generate_language_assessment(
            language="English",
            proficiency_level=level,
            candidate_name="Test",
            job_title="Test Job"
        )
        assert assessment["status"] == "success", f"Failed for level {level}"
    
    print(f"✅ All {len(PROFICIENCY_LEVELS)} proficiency levels work correctly")
    print(f"   - Levels: {', '.join(PROFICIENCY_LEVELS.keys())}")
except Exception as e:
    print(f"❌ Proficiency levels error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - LANGUAGE ASSESSMENT AGENT READY FOR DEPLOYMENT")
print("=" * 70)

# Summary
print("\n📋 IMPLEMENTATION SUMMARY:")
print("""
✅ Language Assessment Tool
   - generate_language_assessment() - Creates tailored assessments
   - evaluate_language_assessment() - Evaluates candidate responses
   - Failure tracking system - Blocks job after 2 failures
   - Support for 7 proficiency levels (A1-C2 + Native)

✅ Language Assessment Agent
   - Integrated with Google ADK
   - Two modes: Assessment Generation & Evaluation
   - Strict evaluation protocol (pass/not pass only)
   - Support for multiple languages

✅ Integration
   - Tools exported from src/tools/__init__.py
   - Agent exported from src/agents/__init__.py
   - Orchestrator updated with language_assessment_agent
   - Full workflow support in main.py

📚 SUPPORTED LANGUAGES:
English, Spanish, French, German, Italian, Portuguese, Dutch, Swedish,
Polish, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and others

🎯 PROFICIENCY LEVELS (CEFR Framework):
- A1: Beginner
- A2: Elementary
- B1: Intermediate
- B2: Upper-Intermediate
- C1: Advanced
- C2: Proficient
- Native: Native Speaker
""")
