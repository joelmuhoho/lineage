from tests.utils import login_test_user_1
from flask import url_for

def test_index(client, test_user_1):
    login_test_user_1(client, test_user_1)

    response = client.get(url_for("family.index"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Create Family" in response.data