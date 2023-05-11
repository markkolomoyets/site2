from UserLogin import UserLogin
from flask import Flask, redirect, url_for
from flask_login import  current_user
from functools import wraps

def special_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.getAdmin() != 'admin':  # Перевіряємо роль користувача
            return redirect(url_for('hello_world'))
        return func(*args, **kwargs)
    return decorated_view