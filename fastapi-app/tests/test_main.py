from datetime import datetime

def test_get_todos_with_items():
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        completed=False,
        due_date=datetime.now()  # 필수 필드 추가
    )
    save_todos([todo.dict()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"

def test_update_todo():
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        completed=False,
        due_date=datetime.now()  # 필수 필드 추가
    )
    save_todos([todo.dict()])
    updated_todo = {
        "id": 1,
        "title": "Updated",
        "description": "Updated description",
        "completed": True,
        "due_date": datetime.now().isoformat()  # API 요청용 문자열 포맷
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_delete_todo():
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        completed=False,
        due_date=datetime.now()  # 필수 필드 추가
    )
    save_todos([todo.dict()])
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
