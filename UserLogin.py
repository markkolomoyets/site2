from flask_login import UserMixin
from flask import url_for
import time
import uuid
from imghdr import what
class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "Без імені"

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"

    def getAdmin(self):
        return 'admin' if self.__user['admin'] == 1 else "user"

    def getTime(self):
        return time.strftime('%d.%m.%Y %H:%M', time.localtime(self.__user['time'])) if self.__user else "Без дати"

    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/avatar/ico_user.png'), "rb") as f:
                    img = f.read()

            except FileNotFoundError as e:
                print("!!! аватар по замовчуванню не знайден")
        else:
            img = self.__user['avatar']
        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or \
           ext == "PNG" or \
           ext == "jpg" or \
           ext == "JPG":
            return True
        return False
