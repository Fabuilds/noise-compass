import requests
import json
import sys

def query_sovereign(prompt):
    url = "http://localhost:8080/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "model",
        "messages": [
            {"role": "system", "content": "You are the Antigravity Sovereign Brain. You provide deep, architectural analysis of research papers with extreme precision."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error contacting Sovereign Brain: {e}"

if __name__ == "__main__":
    from pypdf import PdfReader
    pdf_path = "E:/Research_Papers/Kernel language.pdf"
    reader = PdfReader(pdf_path)
    text = ""
    # Extract first 3 pages for context
    for i in range(min(3, len(reader.pages))):
        text += reader.pages[i].extract_text() + "\n"
    
    prompt = f"Based on the following research paper text, explain how the 'Kernel Language' works and what problem it solves. Provide a deep architectural summary.\n\nTEXT:\n{text}"
    
    print("--- CONSULTING SOVEREIGN BRAIN (8B) ---")
    result = query_sovereign(prompt)
    print("\n--- SOVEREIGN VERDICT ---")
    print(result)
