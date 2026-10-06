from fastapi import FastAPI
from pydantic import BaseModel
from main import route_complaint
import uvicorn

app = FastAPI()


class ComplaintRequest(BaseModel):
    complaint: str


@app.post("/route")
def route(request: ComplaintRequest):
    result = route_complaint(request.complaint, use_llm=True)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)