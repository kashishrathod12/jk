from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_methods=["*"],
allow_headers=["*"]
)

# ---------- CSV API ----------

df = pd.read_csv("q-fastapi.csv")

@app.get("/api")
async def get_students(
class_: Optional[List[str]] = Query(None, alias="class")
):
data = df


if class_:
    data = df[df["class"].isin(class_)]

return {
    "students": data.to_dict(orient="records")
}


# ---------- Sentiment API ----------

class SentimentRequest(BaseModel):
sentences: List[str]

@app.post("/sentiment")
async def sentiment(req: SentimentRequest):
positive = [
"love","great","excellent","amazing","awesome",
"good","happy","fantastic","wonderful","best",
"like","enjoy","nice","perfect"
]


negative = [
    "hate","terrible","bad","awful","worst",
    "sad","angry","disappointed","horrible",
    "poor","upset"
]

results = []

for sentence in req.sentences:
    text = sentence.lower()

    pos = sum(word in text for word in positive)
    neg = sum(word in text for word in negative)

    if pos > neg:
        label = "happy"
    elif neg > pos:
        label = "sad"
    else:
        label = "neutral"

    results.append({
        "sentence": sentence,
        "sentiment": label
    })

return {"results": results}
