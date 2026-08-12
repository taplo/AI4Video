"""Tests for UserView — covers UserView.py (556 stmts)."""
import json
import time
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from django.test import RequestFactory
from datetime import datetime


def _mock_session(user_id=1, username="admin", with_captcha=False):
    session = MagicMock()
    data = {}
    if user_id:
        data["user"] = {"id": user_id, "username": username}
    if with_captcha:
        data["captcha_key"] = {"captcha_text": "ABCD", "captcha_create_timestamp": int(time.time())}
    session.get = lambda key, default=None: data.get(key, default)
    session.__getitem__ = lambda self, key: data[key]
    session.__contains__ = lambda self, key: key in data
    session.has_key = lambda key: key in data
    session.__delitem__ = lambda self, key: data.pop(key, None)
    return session


def _make_request(method, path, data=None, user_id=1, with_captcha=False, **kwargs):
    factory = RequestFactory()
    if method == "GET":
        request = factory.get(path, data or {}, **kwargs)
    else:
        content_type = kwargs.pop("content_type", "application/json")
        body = json.dumps(data) if isinstance(data, dict) else data
        request = factory.post(path, data=body, content_type=content_type, **kwargs)
    request.session = _mock_session(user_id=user_id, with_captcha=with_captcha)
    return request


# ===================== random_color =====================

class TestRandomColor:
    def test_returns_tuple_of_3(self):
        from app.views.UserView import random_color
        r, g, b = random_color()
        assert isinstance(r, int)
        assert isinstance(g, int)
        assert isinstance(b, int)

    def test_custom_range(self):
        from app.views.UserView import random_color
        for _ in range(50):
            r, g, b = random_color(100, 200)
            assert 100 <= r <= 200
            assert 100 <= g <= 200
            assert 100 <= b <= 200


# ===================== generate_secure_captcha =====================

class TestGenerateSecureCaptcha:
    def test_returns_text_and_image(self):
        from app.views.UserView import generate_secure_captcha
        text, image = generate_secure_captcha()
        assert isinstance(text, str)
        assert len(text) == 4
        assert image.size == (120, 40)

    def test_custom_length(self):
        from app.views.UserView import generate_secure_captcha
        text, image = generate_secure_captcha(length=6)
        assert len(text) == 6

    def test_chars_are_valid(self):
        from app.views.UserView import generate_secure_captcha
        valid_chars = set("ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789")
        text, _ = generate_secure_captcha()
        for c in text:
            assert c in valid_chars


# ===================== api_openIndex =====================

class TestApiOpenIndex:
    def test_get_success(self):
        from app.views.UserView import api_openIndex
        request = _make_request("GET", "/user/openIndex")
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.count.return_value = 0
            mock_user.objects.order_by.return_value.values.return_value.__getitem__ = MagicMock(return_value=[])
            with patch("app.views.UserView.buildPageLabels", return_value=[]):
                response = api_openIndex(request)
                data = json.loads(response.content)
                assert data["code"] == 1000

    def test_post_not_supported(self):
        from app.views.UserView import api_openIndex
        request = _make_request("POST", "/user/openIndex", data={})
        response = api_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_no_auth(self):
        from app.views.UserView import api_openIndex
        request = _make_request("GET", "/user/openIndex", user_id=None)
        response = api_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_with_pagination(self):
        from app.views.UserView import api_openIndex
        request = _make_request("GET", "/user/openIndex", {"p": "1", "ps": "5"})
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.count.return_value = 10
            mock_user.objects.order_by.return_value.values.return_value.__getitem__ = MagicMock(return_value=[])
            with patch("app.views.UserView.buildPageLabels", return_value=[]):
                response = api_openIndex(request)
                data = json.loads(response.content)
                assert data["code"] == 1000
                assert data["pageData"]["page_size"] == 5


# ===================== api_openAdd =====================

class TestApiOpenAdd:
    def test_post_valid(self):
        from app.views.UserView import api_openAdd
        request = _make_request("POST", "/user/openAdd", data={
            "username": "testuser",
            "email": "test@test.com",
            "password": "pass123456",
            "is_active": "1",
        })
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.filter.return_value.exists.return_value = False
            mock_user_instance = MagicMock()
            mock_user_instance.id = 1
            mock_user.return_value = mock_user_instance
            with patch("app.views.UserView.LogUtils") as mock_log:
                response = api_openAdd(request)
                data = json.loads(response.content)
                assert data["code"] == 1000

    def test_post_empty_username(self):
        from app.views.UserView import api_openAdd
        request = _make_request("POST", "/user/openAdd", data={
            "username": "",
            "email": "test@test.com",
            "password": "pass123456",
            "is_active": "1",
        })
        with patch("app.views.UserView.User") as mock_user:
            response = api_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_duplicate_username(self):
        from app.views.UserView import api_openAdd
        request = _make_request("POST", "/user/openAdd", data={
            "username": "existing",
            "email": "test@test.com",
            "password": "pass123456",
            "is_active": "1",
        })
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.filter.return_value.exists.return_value = True
            response = api_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_short_password(self):
        from app.views.UserView import api_openAdd
        request = _make_request("POST", "/user/openAdd", data={
            "username": "testuser",
            "email": "test@test.com",
            "password": "123",
            "is_active": "1",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.UserView import api_openAdd
        request = _make_request("GET", "/user/openAdd")
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0


# ===================== api_openEdit =====================

class TestApiOpenEdit:
    def test_post_valid_no_password_change(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "1",
            "username": "admin",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "",
            "re_password": "",
        })
        with patch("app.views.UserView.User") as mock_user:
            mock_obj = MagicMock()
            mock_obj.username = "admin"
            mock_user.objects.filter.return_value.first.return_value = mock_obj
            with patch("app.views.UserView.LogUtils") as mock_log:
                response = api_openEdit(request)
                data = json.loads(response.content)
                assert data["code"] == 1000

    def test_post_valid_with_password(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "1",
            "username": "admin",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "newpass123",
            "re_password": "newpass123",
        })
        with patch("app.views.UserView.User") as mock_user:
            mock_obj = MagicMock()
            mock_obj.username = "admin"
            mock_user.objects.filter.return_value.first.return_value = mock_obj
            with patch("app.views.UserView.LogUtils") as mock_log:
                response = api_openEdit(request)
                data = json.loads(response.content)
                assert data["code"] == 1000

    def test_post_password_mismatch(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "1",
            "username": "admin",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "pass1",
            "re_password": "pass2",
        })
        response = api_openEdit(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_user_not_found(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "999",
            "username": "admin",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "",
            "re_password": "",
        })
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.filter.return_value.first.return_value = None
            response = api_openEdit(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_empty_username(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "1",
            "username": "",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "",
            "re_password": "",
        })
        response = api_openEdit(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_new_password_required(self):
        from app.views.UserView import api_openEdit
        request = _make_request("POST", "/user/openEdit", data={
            "id": "1",
            "username": "admin",
            "email": "admin@test.com",
            "is_active": "1",
            "new_password": "",
            "re_password": "somepass",
        })
        response = api_openEdit(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.UserView import api_openEdit
        request = _make_request("GET", "/user/openEdit")
        response = api_openEdit(request)
        data = json.loads(response.content)
        assert data["code"] == 0


# ===================== api_openDel =====================

class TestApiOpenDel:
    def test_post_valid(self):
        from app.views.UserView import api_openDel
        request = _make_request("POST", "/user/openDel", data={"id": "2"})
        with patch("app.views.UserView.User") as mock_user:
            mock_obj = MagicMock()
            mock_obj.is_superuser = 0
            mock_obj.delete.return_value = True
            mock_user.objects.filter.return_value.__len__ = MagicMock(return_value=1)
            mock_user.objects.filter.return_value.__getitem__ = MagicMock(return_value=mock_obj)
            with patch("app.views.UserView.f_sessionReadUser", return_value={"id": 1}):
                with patch("app.views.UserView.LogUtils"):
                    response = api_openDel(request)
                    data = json.loads(response.content)
                    assert data["code"] == 1000

    def test_post_cannot_delete_self(self):
        from app.views.UserView import api_openDel
        request = _make_request("POST", "/user/openDel", data={"id": "1"})
        with patch("app.views.UserView.f_sessionReadUser", return_value={"id": 1}):
            response = api_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_cannot_delete_superuser(self):
        from app.views.UserView import api_openDel
        request = _make_request("POST", "/user/openDel", data={"id": "2"})
        with patch("app.views.UserView.User") as mock_user:
            mock_obj = MagicMock()
            mock_obj.is_superuser = 1
            mock_user.objects.filter.return_value.__len__ = MagicMock(return_value=1)
            mock_user.objects.filter.return_value.__getitem__ = MagicMock(return_value=mock_obj)
            with patch("app.views.UserView.f_sessionReadUser", return_value={"id": 1}):
                response = api_openDel(request)
                data = json.loads(response.content)
                assert data["code"] == 0

    def test_post_user_not_found(self):
        from app.views.UserView import api_openDel
        request = _make_request("POST", "/user/openDel", data={"id": "999"})
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.filter.return_value.__len__ = MagicMock(return_value=0)
            with patch("app.views.UserView.f_sessionReadUser", return_value={"id": 1}):
                response = api_openDel(request)
                data = json.loads(response.content)
                assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.UserView import api_openDel
        request = _make_request("GET", "/user/openDel")
        response = api_openDel(request)
        data = json.loads(response.content)
        assert data["code"] == 0


# ===================== api_openInfo =====================

class TestApiOpenInfo:
    def test_get_valid(self):
        from app.views.UserView import api_openInfo
        request = _make_request("GET", "/user/openInfo", {"id": "1"})
        with patch("app.views.UserView.User") as mock_user:
            mock_obj = MagicMock()
            mock_obj.id = 1
            mock_obj.username = "admin"
            mock_obj.email = "admin@test.com"
            mock_obj.is_active = 1
            mock_obj.is_superuser = 0
            mock_obj.is_staff = 1
            mock_obj.date_joined = datetime(2026, 1, 1)
            mock_obj.last_login = datetime(2026, 1, 2)
            mock_user.objects.filter.return_value.first.return_value = mock_obj
            response = api_openInfo(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert data["info"]["username"] == "admin"

    def test_get_not_found(self):
        from app.views.UserView import api_openInfo
        request = _make_request("GET", "/user/openInfo", {"id": "999"})
        with patch("app.views.UserView.User") as mock_user:
            mock_user.objects.filter.return_value.first.return_value = None
            response = api_openInfo(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_get_missing_id(self):
        from app.views.UserView import api_openInfo
        request = _make_request("GET", "/user/openInfo")
        response = api_openInfo(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_not_supported(self):
        from app.views.UserView import api_openInfo
        request = _make_request("POST", "/user/openInfo", data={"id": "1"})
        response = api_openInfo(request)
        data = json.loads(response.content)
        assert data["code"] == 0


# ===================== api_openCaptcha =====================

class TestApiOpenCaptcha:
    def test_returns_png(self):
        from app.views.UserView import api_openCaptcha
        request = _make_request("GET", "/user/captcha")
        response = api_openCaptcha(request)
        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"


# ===================== login =====================

class TestLogin:
    def test_get_renders_login(self):
        from app.views.UserView import login
        request = _make_request("GET", "/login")
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            mock_config.logDebug = False
            response = login(request)
            assert response.status_code == 200

    def test_post_valid_login(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "pass123456",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            mock_config.logDebug = False
            with patch("app.views.UserView.User") as mock_user:
                mock_obj = MagicMock()
                mock_obj.id = 1
                mock_obj.is_active = True
                mock_obj.check_password.return_value = True
                mock_obj.is_superuser = 0
                mock_obj.is_staff = 1
                mock_obj.first_name = "cec=0"
                mock_user.objects.filter.return_value.first.return_value = mock_obj
                with patch("app.views.UserView.LogUtils"):
                    response = login(request)
                    data = json.loads(response.content)
                    assert data["code"] == 1000

    def test_post_wrong_password(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "wrongpass",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            mock_config.logDebug = False
            with patch("app.views.UserView.User") as mock_user:
                mock_obj = MagicMock()
                mock_obj.id = 1
                mock_obj.is_active = True
                mock_obj.check_password.return_value = False
                mock_obj.first_name = "cec=0"
                mock_user.objects.filter.return_value.first.return_value = mock_obj
                response = login(request)
                data = json.loads(response.content)
                assert data["code"] == 0
                assert "cec=1" in mock_obj.first_name

    def test_post_wrong_password_lock(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "wrongpass",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            mock_config.logDebug = False
            with patch("app.views.UserView.User") as mock_user:
                mock_obj = MagicMock()
                mock_obj.id = 1
                mock_obj.is_active = True
                mock_obj.check_password.return_value = False
                mock_obj.first_name = "cec=6"
                mock_user.objects.filter.return_value.first.return_value = mock_obj
                response = login(request)
                data = json.loads(response.content)
                assert data["code"] == 0
                assert mock_obj.is_active is False

    def test_post_user_not_registered(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "nouser",
            "password": "pass123",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            with patch("app.views.UserView.User") as mock_user:
                mock_user.objects.filter.return_value.first.return_value = None
                response = login(request)
                data = json.loads(response.content)
                assert data["code"] == 0

    def test_post_missing_params(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "",
            "password": "",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            response = login(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_locked_account(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "pass123",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = False
            mock_config.logDebug = False
            with patch("app.views.UserView.User") as mock_user:
                mock_obj = MagicMock()
                mock_obj.id = 1
                mock_obj.is_active = False
                mock_user.objects.filter.return_value.first.return_value = mock_obj
                response = login(request)
                data = json.loads(response.content)
                assert data["code"] == 0

    def test_post_captcha_missing(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "pass123",
        })
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = True
            response = login(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_captcha_expired(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "pass123",
            "captcha": "ABCD",
        }, with_captcha=True)
        request.session.get = lambda key, default=None: (
            {"captcha_text": "ABCD", "captcha_create_timestamp": int(time.time()) - 400}
            if key == "captcha_key" else default
        )
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = True
            response = login(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_captcha_incorrect(self):
        from app.views.UserView import login
        request = _make_request("POST", "/login", data={
            "username": "admin",
            "password": "pass123",
            "captcha": "WRONG",
        }, with_captcha=True)
        request.session.get = lambda key, default=None: (
            {"captcha_text": "ABCD", "captcha_create_timestamp": int(time.time())}
            if key == "captcha_key" else default
        )
        with patch("app.views.UserView.g_config") as mock_config:
            mock_config.isEnableLoginCaptcha = True
            response = login(request)
            data = json.loads(response.content)
            assert data["code"] == 0


# ===================== logout =====================

class TestLogout:
    def test_logout_clears_session(self):
        from app.views.UserView import logout
        request = _make_request("GET", "/logout")
        request.session = MagicMock()
        request.session.has_key = MagicMock(side_effect=lambda k: k == "user")
        request.session.get = MagicMock(return_value={"id": 1, "username": "admin"})
        request.session.__delitem__ = MagicMock()
        with patch("app.views.UserView.LogUtils"):
            response = logout(request)
            assert response.status_code == 302

    def test_logout_no_session_user(self):
        from app.views.UserView import logout
        request = _make_request("GET", "/logout")
        request.session = MagicMock()
        request.session.has_key = MagicMock(return_value=False)
        request.session.__delitem__ = MagicMock()
        response = logout(request)
        assert response.status_code == 302
