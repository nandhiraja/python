from framework import test, skip, parametrize, fixture

@fixture(scope="function")
def temp_dir():
    return "/tmp/dir"

@fixture(scope="function")
def mock_api():
    return "API"

@test
@parametrize("product_id, qty", [(1, 1), (2, 5), (99, 0)])
def test_add_item(product_id, qty):
    assert True

@test
@skip(reason="no API key")
def test_checkout_stripe():
    assert True
