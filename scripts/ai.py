# This script allows you to infer an OpenRouter LLM to evaluate the LLMs response. It will just tell you what it thinks, it won't auto-evaluate the LLM.



import os, re, json, time
import requests



URL = config["openrouter_address"]
API_KEY = config["openrouter_key"]

JUDGE_MODEL = config["judge_model"]
JUDGE_SYSTEM = config["judge_system_prompt"]

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "LLM Benchmarking",
}



def chat(model, messages, temperature=0.0, max_tokens=2048, retries=4):
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    
    for attempt in range(retries):
        try:
            r = requests.post(URL, headers=HEADERS, json=payload, timeout=600)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data["choices"][0]["message"].get("content") or ""
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)



message = f"""
## Question given to the model
{question}

## Intended answer and/or scoring for the question
{answer}

## Model response to grade
{response}
"""
print(chat(JUDGE_MODEL, [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": message}]))