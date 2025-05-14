from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Prometheus 메트릭스 엔드포인트 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    due_date: str  # 마감 날짜 필드 추가

# JSON 파일 경로
TODO_FILE = "todo.json"

# JSON 파일에서 To-Do 항목 로드
from datetime import datetime

# JSON 파일에서 To-Do 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            todos = json.load(file)
            today = datetime.now()
            for todo in todos:
                # 날짜 형식이 여러 가지일 수 있으므로 변환을 시도
                try:
                    due_date = datetime.strptime(todo['due_date'], "%Y-%m-%d")
                except ValueError:
                    try:
                        # 다른 형식 시도 (예: 'YYYY/MM/DD')
                        due_date = datetime.strptime(todo['due_date'], "%Y/%m/%d")
                    except ValueError:
                        # 잘못된 형식이거나 파싱할 수 없는 날짜인 경우 기본값을 설정 (예: 현재 날짜)
                        due_date = today
                if due_date < today:
                    todo['completed'] = True
            return todos
    return []


# JSON 파일에 To-Do 항목 저장
def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4)

# To-Do 목록 조회
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# 신규 To-Do 항목 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do 항목 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.dict())  # 업데이트된 항목을 반영
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding='utf-8') as file:  # encoding='utf-8' 추가
        content = file.read()
    return HTMLResponse(content=content)

# 검색 기능 추가
@app.get("/todos/search", response_model=list[TodoItem])
def search_todos(query: str):
    todos = load_todos()
    filtered_todos = [todo for todo in todos if query.lower() in todo["title"].lower() or query.lower() in todo["description"].lower()]
    return filtered_todos
