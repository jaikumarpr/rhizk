import json
import os
import asyncio
import openai
import re

# openai.api_key = os.getenv('OPEN_API_KEY')
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY_RHIZK'))

data_json = {
        "WBS": [
            {
                "PMINumber": "1",
                "Type": "WBS Level",
                "Name": "Site Preparation",
                "Children": [
                    {
                        "PMINumber": "1.1",
                        "Type": "WBS Level",
                        "Name": "Site Survey",
                        "Children": [
                            {
                                "PMINumber": "1.1.1",
                                "Type": "Activity",
                                "Name": "Topographic Survey",
                                "Duration": 3,
                                "ThreePointEstimate": {
                                    "Optimistic": 2,
                                    "MostLikely": 3,
                                    "Pessimistic": 4
                                },
                                "Predecessors": []
                            },
                            {
                                "PMINumber": "1.1.2",
                                "Type": "Activity",
                                "Name": "Soil Testing",
                                "Duration": 2,
                                "ThreePointEstimate": {
                                    "Optimistic": 1,
                                    "MostLikely": 2,
                                    "Pessimistic": 3
                                },
                                "Predecessors": ["1.1.1"]
                            }
                        ]
                    }
                ]
            }

        ]

    }


def get_prompt(type: str):

    prompt = f"""
    You have vast experience in project scheduling in construction industry. come up with a construction schedule for a {type} with 100 activities with relationships between the schedules. 
    
    Make sure activities are grouped under realistic work break down structure. Activity relationship should be sensible, try to come up with a bit complex relationship graph but has a sensible critical path.
    Each activity should consist of duration, predecessors and also three point estimate values ( optimistic, most likely and pessimistic durations). 
    Be realistic about three point estimate. 
    Use the the context of the activity to understand the inherent risk associated with it along with base line estimation and base line critical path to calculate Three point estimate.
    
    
    
    Sample Output json format:
    
    {json.dumps(data_json)}
    
    """

    return prompt


async def askopenai(prompt):

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an exceptional project scheduler in construction industry with all knowledge of risk associated with activities"},
            {"role": "user", "content": prompt}
        ]
    )

    output_text = response.choices[0].message.content
    
    return output_text

def extract_json_from_text(text):
    # Use regular expressions to find the JSON content within the text
    json_match = re.search(r'```json(.*?)```', text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(1).strip()  # Extract and clean the JSON part
        try:
            # Parse the JSON string to a Python dictionary
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return None
    else:
        print("No JSON content found in the text.")
        return None


async def get_schedule(type):
    prompt = get_prompt(type)
    content = await askopenai(prompt)
    json_data = extract_json_from_text(content)
    return json_data
