from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import traceback
import sys
from io import StringIO
import os
import json

from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str


def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code, {})
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}
    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }
    finally:
        sys.stdout = old_stdout


def analyze_error_with_ai(code: str, tb: str):
    client = OpenAI(
        api_key=os.getenv("AIPIPE_TOKEN"),
        base_url="https://aipipe.org/openai/v1"
    )

    prompt = f"""
Identify the Python source code line numbers that caused the error.

Code:
{code}

Traceback:
{tb}

Return JSON:
{{"error_lines":[1,2]}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4.1-nano",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        return data.get("error_lines", [])
    except Exception:
        import re
        matches = re.findall(r'line (\d+)', tb)
        return [int(matches[-1])] if matches else []


@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(req: CodeRequest):

    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    error_lines = analyze_error_with_ai(
        req.code,
        result["output"]
    )

    return {
        "error": error_lines,
        "result": result["output"]
    }