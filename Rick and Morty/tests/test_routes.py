import pytest
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

@patch('app.services.requests.get')
def test_characters_page(mock_get, client):
    """Test the characters page with a mocked API call."""
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = {
        "info": {"count": 1},
        "results": [{"id": 1, "name": "Rick Sanchez", "status": "Alive", "species": "Human"}]
    }
    mock_get.return_value.raise_for_status.return_value = None

    response = client.get('/personagens')
    assert response.status_code == 200
    assert b"Rick Sanchez" in response.data
    assert b"Human" in response.data

@patch('app.services.requests.get')
def test_episodes_page(mock_get, client):
    """Test the episodes page with a mocked API call."""
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = {
        "info": {"count": 1},
        "results": [{"id": 1, "name": "Pilot", "air_date": "December 2, 2013", "episode": "S01E01"}]
    }
    mock_get.return_value.raise_for_status.return_value = None

    response = client.get('/episodios')
    assert response.status_code == 200
    assert b"Pilot" in response.data
    assert b"S01E01" in response.data

@patch('app.services.requests.get')
def test_quiz_page(mock_get, client):
    """Test the quiz page with mocked API calls."""
    # Mock the first call to get character count
    mock_get.side_effect = [
        type('Response', (), {
            'ok': True,
            'raise_for_status': lambda: None,
            'json': lambda: {"info": {"count": 826}}
        }),
        type('Response', (), {
            'ok': True,
            'raise_for_status': lambda: None,
            'json': lambda: [
                {"id": 1, "name": "Rick Sanchez"},
                {"id": 2, "name": "Morty Smith"},
                {"id": 3, "name": "Summer Smith"}
            ]
        })
    ]

    response = client.get('/quiz')
    assert response.status_code == 200
    assert b"Rick Sanchez" in response.data
    assert b"Morty Smith" in response.data
    assert b"Summer Smith" in response.data
