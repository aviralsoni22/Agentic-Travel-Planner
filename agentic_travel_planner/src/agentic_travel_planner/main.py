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
        'destination': 'Panaji, Goa, India',
        'start_date': '2026-01-10',
        'end_date': '2026-01-13',
        'trip_duration': int('3'), #number of nights (if duration = 3 then its 3 nights/ 4 days)
        'num_travelers': int('2'),
        'budget': 1500,
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
