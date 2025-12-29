#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from agentic_travel_planner.crew import AgenticTravelPlanner

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'source': 'New Delhi, India',
        'destination': 'Mumbai, Maharashtra, India',
        'start_date': '2026-03-10',
        'end_date': '2026-03-13',
        'num_travelers': int('2'),
        'budget': 1500,
        'interests': "clubs, food, forts, Beaches",
        'group_category': 'Boys only',
        'currency': 'USD'
    }

    try:
        result = AgenticTravelPlanner().crew().kickoff(inputs=inputs)
        print("\n\n=== FINAL PLAN ===\n\n")
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__=="__main__":
     run()
