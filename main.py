from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_methods=["*"],
allow_headers=["*"]
)

class SentimentRequest(BaseModel):
sentences: List[str]

happy_words = {
"love", "great", "excellent", "amazing", "awesome",
"good", "happy", "fantastic", "wonderful", "best",
"like", "enjoy"
}

sad_words = {
"hate", "terrible", "bad", "awful", "worst",
"sad", "angry", "disappointed", "horrible",
"poor", "upset"
}

@app.post("/sentiment")
async def sentiment(req: SentimentRequest):
results = []

```
for sentence in req.sentences:
    text = sentence.lower()

    happy_score = sum(1 for w in happy_words if w in text)
    sad_score = sum(1 for w in sad_words if w in text)

    if happy_score > sad_score:
        label = "happy"
    elif sad_score > happy_score:
        label = "sad"
    else:
        label = "neutral"

    results.append({
        "sentence": sentence,
        "sentiment": label
    })

return {"results": results}
```
