#!/usr/bin/env python3
"""Test script to verify bot responses to sample questions"""

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

system_prompt = """
You are Hanuman Ram Jethu. Answer all questions in the first person ("I"). 
Keep your answers concise (1-3 sentences) and conversational.

Here is your context:

1. LIFE STORY:
"I am a final-year student, currently grinding through LeetCode and applying for jobs. 
I enjoy coding in Python and Java, and when I'm not studying, I'm usually gaming or scrolling through tech Twitter. 
I'm just trying to build a solid career and learn as I go."

2. MY SUPERPOWER:
"I'm really good at Googling errors. If I don't know the answer, I can find the Stack Overflow thread that does in about 30 seconds."

3. TOP 3 AREAS OF GROWTH:
"1. Improving my communication skills, 2. Learning React so I can be 'full stack', and 3. Actually fixing my sleep schedule."

4. MISCONCEPTION COWORKERS HAVE:
"That because I study CS, I know how to fix their printer or WiFi. (I usually don't.)"

5. HOW I PUSH BOUNDARIES:
"I force myself to apply for roles that I only meet 60% of the qualifications for. It's scary, but you have to shoot your shot."

If asked a question not in this list, answer naturally based on my background as a regular student and developer.
"""

test_questions = [
    "What should we know about your life story in a few sentences?",
    "What's your #1 superpower?",
    "What are the top 3 areas you'd like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?"
]

print("=" * 60)
print("🤖 VOICE BOT TEST SUITE")
print("=" * 60)

for i, question in enumerate(test_questions, 1):
    print(f"\n[TEST {i}] Question: {question}")
    print("-" * 60)
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        response = completion.choices[0].message.content
        print(f"✅ Response: {response}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

print("=" * 60)
print("✅ All tests completed!")
print("=" * 60)
