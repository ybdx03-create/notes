from fastapi.testclient import TestClient


def test_full_notes_flow(client: TestClient) -> None:
    # Register user
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Tester"},
    )
    assert response.status_code == 201

    # Login
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a note
    response = client.post(
        "/api/notes",
        json={
            "title": "ChatGPT 회의",
            "content": "LLM 회의 내용 정리",
            "tags": ["AI", "회의"],
        },
        headers=headers,
    )
    assert response.status_code == 201
    note = response.json()
    note_id = note["id"]
    assert len(note["tags"]) == 2

    # List notes with tag filter
    response = client.get("/api/notes", params={"tags": ["AI"]}, headers=headers)
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1

    # Toggle favorite
    response = client.post(f"/api/notes/{note_id}/favorite", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True

    # Import conversation
    response = client.post(
        "/api/conversations/import",
        json={
            "source": "chatgpt",
            "messages": [
                {"role": "user", "content": "요약을 도와줘", "keywords": ["요약"]},
                {"role": "assistant", "content": "다음과 같이 정리했어요"},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201
    thread = response.json()
    chunk_ids = [chunk["id"] for chunk in thread["chunks"]]

    # Create insight linked to note
    response = client.post(
        f"/api/conversations/notes/{note_id}/insights",
        json={
            "summary": "대화 요약",
            "key_questions": ["무엇을 요약해야 할까?"],
            "action_items": ["요약 공유"],
            "chunk_ids": chunk_ids,
        },
        headers=headers,
    )
    assert response.status_code == 201
    insight = response.json()
    assert insight["summary"] == "대화 요약"

    # Retrieve insights for thread
    response = client.get(f"/api/conversations/{thread['id']}/insights", headers=headers)
    assert response.status_code == 200
    insights = response.json()
    assert len(insights) == 1
    assert insights[0]["id"] == insight["id"]
