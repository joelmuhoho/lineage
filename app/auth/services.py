from app.models.user import User
from config import Config
from app.user.services import UserService
from typing import Union, Tuple, Optional
from flask_login import login_user, current_user
from flask import session
from app.services.service_base import service_response

class AuthService:

    @staticmethod
    def authenticate(email: str, password: str) -> Union[User, Tuple[dict, int]]:
        user_service = UserService()

        data, status = user_service.get_user(email=email)
        user = data.get('data')
        if user and user.check_password(password):
            login_user(user)
            AuthService.set_current_family_id()
            return service_response(200, 'Login successful', 'success', user)
        return service_response(403, 'Invalid username or password', 'danger', None)

    @staticmethod
    def get_guest_info()-> Tuple[str, str, str]:
        """Get guest user information."""
        return Config.GUEST_NAME,Config.GUEST_EMAIL,Config.GUEST_PASSWORD

    @staticmethod
    def set_current_family_id(current_family_id: Optional[int] = None):
        """Set the current family ID for the current user."""
        if current_user.is_authenticated:
            families_length = len(current_user.families)
            if families_length == 1:
                session['current_family_id'] = current_user.families[0].family_id
            elif families_length > 1 and current_family_id:
                session['current_family_id'] = current_family_id
            return session
        return None