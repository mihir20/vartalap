from meta_ai_api import MetaAI
from openai import OpenAI
import os

prompt = '''
You are an AI Meeting Summarizer. Analyze the following meeting transcription and generate a comprehensive summary.

**Transcription:**

{}

**Instructions:**

1.  **Generate a concise summary** of the meeting, highlighting the main topics and key discussions.
2.  **Identify and list all action items**, including who is responsible and any deadlines mentioned. Format them as: "Action Item: [Action], Responsible: [Name], Deadline: [Date]".
3.  **Extract and list all key decisions** made during the meeting.
4.  **List the main speakers** and briefly mention their contributions.
5.  **Identify and list key keywords and topics** discussed.
6.  **Perform sentiment analysis** to determine the overall tone of the meeting (e.g., positive, negative, neutral, mixed).
7.  **Provide a longer more detailed summary** of the meeting.
8.  **If possible, provide a list of questions that were asked, and their answers.**

output should strictly follow specified Output Format

**Output Format:**

**Meeting Summary (Concise):**
[Concise summary here]

**Action Items:**
[Action item list here]

**Key Decisions:**
[Decision list here]

**Speakers:**
[Speaker list here]

**Keywords/Topics:**
[Keyword/topic list here]

**Sentiment Analysis:**
[Sentiment analysis here]

**Meeting Summary (Detailed):**
[Detailed summary here]

**Questions and Answers:**
[Question and answer list here]
'''

def summarise(transcription, mode="meta_ai"):
    """
    Summarise a meeting transcription using MetaAI.

    Args:
        transcription (str): Meeting transcription

    Returns:
        str: Meeting summary
    """
    if len(transcription) > 28000:
        transcription = transcription[:28000] + "..."

    req_prompt = prompt.format(transcription)
    print(req_prompt)

    # Create a MetaAI instance
    if mode == "meta_ai":
        meta_ai = MetaAI()
        summary = meta_ai.prompt(message=req_prompt)

    if mode == "openai":
        openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": req_prompt}]
        )
        summary = response.choices[0].message.content

    return summary

if __name__ == "__main__":
    # Load the transcription
    with open('summary.txt', 'r', encoding='utf-8') as f:
        transcription = f.read()

    # Summarise the transcription
    summary = summarise(transcription, mode="openai")

    # Print the summary
    print(summary)