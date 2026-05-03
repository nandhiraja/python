from framework import test, fixture

@fixture(scope="session")
def db_connection():
    return "DB_CONN"

@test
def test_login_valid_credentials():
    assert True

@test
def test_login_invalid_password():
    assert True

@test
def test_login_expired_token():
    status = 200
    assert status == 401, "Expected status=401, got status=200"
