import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_blank_registration(client): #tests whether the application accepts a blank registration input, and the expected outcome is a failure

    response = client.post('/register', json={
        "firstName": "",
        "lastName": "",
        "username": "",
        "password": ""
    })

    assert response.status_code == 400


def test_username_contains_spaces(client): #tests whether the application accepts a username that contains spaces, and the expected outcome is a failure

    response = client.post('/register', json={
        "firstName": "John",
        "lastName": "Doe",
        "username": "John Doe",
        "password": "Password123"
    })

    assert response.status_code == 400


def test_password_contains_spaces(client): #tests whether the application accepts a password that contains spaces, and the expected outcome is a failure

    response = client.post('/register', json={
        "firstName": "John",
        "lastName": "Doe",
        "username": "JohnDoe",
        "password": "Password 123"
    })

    assert response.status_code == 400


def test_sql_injection_login(client): #tests whether the application will protect against SQL injection, and the expected outcome is that it will stop any log in attempts using SQL injection
    response = client.post('/login', data={
        "username": "' OR '1'='1",
        "password": "' OR '1'='1"
    }, follow_redirects=True)

    assert b"admin-dashboard" not in response.data
    assert b"standard-dashboard" not in response.data


def test_admin_dashboard_redirect(client): #tests whether the application protects against standard users attempting to access the admin dashboard through changing the URL to '/admin-dashboard' instead of '/standard-dashboard'
    response = client.get('/admin-dashboard')

    assert response.status_code == 302