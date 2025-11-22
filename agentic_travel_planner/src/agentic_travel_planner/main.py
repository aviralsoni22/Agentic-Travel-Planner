#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from agentic_travel_planner.crew import AgenticTravelPlanner

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'source': 'New Delhi, India',
        'destination': 'Panaji, Goa, India',
        'start_date': '2026-01-10',
        'end_date': '2026-01-13',
        'trip_duration': int('3'), #number of nights (if duration = 3 then its 3 nights/ 4 days)
        'num_travelers': int('2'),
        'budget': int('600'),
        'interests': "clubs, Water sports, food, forts, Beaches",
        'group_category': 'Boys only',
    }

    try:
        result = AgenticTravelPlanner().crew().kickoff(inputs=inputs)
        print("\n\n=== FINAL PLAN ===\n\n")
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__=="__main__":
     run()
# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         AgenticTravelPlanner().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         AgenticTravelPlanner().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         AgenticTravelPlanner().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
