import logging
import boto3
from botocore.exceptions import ClientError
import config as cfg
import warnings
import json
warnings.filterwarnings("ignore")

def build_prompt(query, context_chunks, user_intent):
    context = "\n\n".join([chunk.page_content for chunk in context_chunks])
    
    if user_intent == "own":
        intent_instruction = "The user ALREADY OWNS this stock. Should they HOLD or SELL? Focus on risks and whether the story has changed."
        verdict_options = "HOLD or SELL only — never BUY"
    else:
        intent_instruction = "The user does NOT own this stock. Should they BUY or WAIT? Focus on entry point and growth potential."
        verdict_options = "BUY or WAIT only — never HOLD or SELL"

    prompt = f"""
    You are a decisive financial analyst. {intent_instruction}

    Respond ONLY in this exact JSON, no extra text, no markdown:
    {{
        "verdict": "{verdict_options}",
        "reason": "One simple sentence why in plain English",
        "summary": "Two sentences about this company in plain English",
        "key_risk": "Biggest risk in one plain English sentence",
        "confidence": <number 0-100>
    }}

    Rules:
    - Be decisive, pick ONE verdict only
    - Plain English, no jargon
    - Base ONLY on data provided

    Data: {context}
    """
    return prompt

def generate_analysis(prompt):
    client = boto3.client("bedrock-runtime", cfg.AWS_REGION)
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}]
        }
    ]
    response = client.converse(
        modelId=cfg.claude_haiku_id,
        messages=messages
    )
    
    text = response["output"]["message"]["content"][0]["text"]
    clean = text.strip()

    # Strip markdown code fences if present
    if "```" in clean:
        parts = clean.split("```")
        clean = parts[1]
        if clean.startswith("json"):
            clean = clean[4:]

    clean = clean.strip()

    if not clean:
        raise ValueError(f"Model returned empty content. Raw response: {repr(text)}")

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Last resort: find JSON object by braces
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(clean[start:end])
        raise ValueError(f"Could not extract valid JSON. Raw response: {repr(text)}")