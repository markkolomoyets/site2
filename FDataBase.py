import base64
import math
import sqlite3
import time
import hashlib
from imghdr import what
from flask import url_for
from io import BytesIO
from datetime import datetime


class FDataBase:
    def __init__(self, db):
        self.__db  = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM posts'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()

            if res:
                return res
        except:
            print('Помилка читання БД')
        return []


    def addPost(self, title, text, user_id, img):
        try:
            binary_img = sqlite3.Binary(img)
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (title, text, tm, user_id, binary_img))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка додавання в БД")
            return False
        return True


    def getPost(self, postId):
        try:
            self.__cur.execute("SELECT title, text FROM posts WHERE id = ? LIMIT 1", (postId,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Помилка отримання статтї з БД {e}")

        return (False, False)

    def getPostsImg(self, postId):
        try:
            if not postId:
                self.__cur.execute(f"SELECT img FROM posts ORDER BY time DESC")
                res = self.__cur.fetchall()

                if res:
                    return res
            else:
                self.__cur.execute(f"SELECT img FROM posts WHERE id = ? LIMIT 1", (postId,))
                res = self.__cur.fetchall()

                if res:
                    return res

        except sqlite3.Error as e:
            print(f"Помилка отримання статтей з БД {e}")

        return []

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, datetime(time, 'unixepoch') as formatted_time, img FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Помилка отримання статтей з БД {e}")

        return []

    def writePostImg(self,app, results):
        try:

            image_paths = []
            print(results)
            for i, result in enumerate(results):
                image_data = result[0]
                if image_data is None:
                    default_image_path = app.config['UPLOAD_FOLDER'] + '/post/default.JPG'
                    image_path = default_image_path
                else:
                    image_path = app.config['UPLOAD_FOLDER'] + f'/post/post_{i}.png'
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                image_paths.append(image_path)
            return image_paths
        except Exception as e:
            print(f"Помилка завантаження картинок з БД {e}")

            return []

    def writeAvatarImg(self, app, results):
        try:
            image_paths = []
            existing_images = {}
            for i, result in enumerate(results):
                image_data = result[0]
                if image_data is None:
                    default_image_path = app.config['UPLOAD_FOLDER'] + '/avatar/ico_user.png'
                    image_path = default_image_path
                else:
                    # Calculate MD5 hash of the image data
                    image_hash = hashlib.md5(image_data).hexdigest()
                    if image_hash in existing_images:
                        # Use the path of the similar image
                        image_path = existing_images[image_hash]
                    else:
                        image_path = app.config['UPLOAD_FOLDER'] + f'/avatar/avatar_{i}.png'
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        existing_images[image_hash] = image_path
                image_paths.append(image_path)
            return image_paths

        except Exception as e:
            print(f"Помилка завантаження аватара коментаря з БД {e}")
            return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute("SELECT COUNT() as `count` FROM users WHERE email LIKE ?", (email,))
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Користувач з таким email вже існує")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?, ?)", (name, email, hpsw, tm, 0))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Помилка додавання користувача в БД {e}")
            return False
        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайден")
                return False

            return res
        except sqlite3.Error as e:
            print(f'Помилка отримання данних з БД {e}')
        return False

    def getAllUser(self):
        try:
            self.__cur.execute("SELECT * FROM users ")
            res = self.__cur.fetchall()
            if not res:
                print("Користувачів не знайдено")
                return False

            return res
        except sqlite3.Error as e:
            print(f'Помилка отримання данних з БД {e}')
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайден")
                return False

            return res
        except sqlite3.Error as e:
            print(f'Помилка отримання данних з БД {e}')
        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return  False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Помилка оновлення аватара в БД {e}")
            return False
        return True

    def addComments(self, user_id, post_id, comment_text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO comments VALUES(NULL, ?, ?, ?, ?)", (user_id, post_id, comment_text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка додавання коментаря в БД")
            return False
        return True

    def getAvatarComments(self, postId):

        try:
            self.__cur.execute("""SELECT u.avatar 
                                  FROM comments c 
                                  INNER JOIN users u ON c.user_id = u.id 
                                  WHERE c.post_id = ?
                                  ORDER BY c.time DESC""", (postId,))

            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Помилка отримання коментарів з БД {e}")
        return []

    def getComments(self, postId):

        try:
            self.__cur.execute("""SELECT c.comment_text, datetime(c.time, 'unixepoch') as formatted_time, u.id, u.name, u.avatar 
                                  FROM comments c 
                                  INNER JOIN users u ON c.user_id = u.id 
                                  WHERE c.post_id = ?
                                  ORDER BY c.time DESC""", (postId,))

            res = self.__cur.fetchall()

            if res:
                return res
        except sqlite3.Error as e:
            print(f"Помилка отримання коментарів з БД {e}")

        return []

    def getAvatarUser(self, app, user_id):
        try:
            self.__cur.execute("SELECT avatar FROM users WHERE id = ? LIMIT 1", (user_id,))
            res = self.__cur.fetchone()

            if res is None:
                print("Аватар не знайдено")
                return None

            avatar_blob = res[0]
            avatar_base64 = base64.b64encode(avatar_blob).decode('utf-8')

            return avatar_base64

        except sqlite3.Error as e:
            print(f"Помилка отримання аватара з БД: {e}")

        return None

