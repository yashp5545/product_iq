from openai import OpenAI
import os

def openai(prompt, system_message):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content