from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некоректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField("Запам'ятати", default=False)
    submit = SubmitField("Увійти")

class RegisterForm(FlaskForm):
    name = StringField("Ім'я: ", validators=[Length(min=4, max=25, message="Ім'я має бути min-4 max-25")])
    email = StringField("Email: ", validators=[Email("Некоректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль має бути не менше 4 символів і не більше 100")])
    psw2 = PasswordField("Повтор пароль: ", validators=[DataRequired(), EqualTo('psw', message="Паролі не співпадають")])
    submit = SubmitField("Реєстрація")