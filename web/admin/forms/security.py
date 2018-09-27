# -*- coding: utf-8 -*-

from flask.ext.security.forms import LoginForm, RegisterForm, EqualTo, \
    password_required, email_required, email_validator, unique_user_email
from wtforms import StringField, BooleanField, SubmitField, PasswordField

_default_field_labels = {
    'email': u'Электронная почта',
    'password': u'Пароль',
    'remember_me': u'Запомнить меня',
    'login': u'Войти',
    'retype_password': u'Повторить пароль',
    'register': u'Зарегистрироваться',
    'send_confirmation': 'Resend Confirmation Instructions',
    'recover_password': 'Recover Password',
    'reset_password': 'Reset Password',
    'new_password': 'New Password',
    'change_password': 'Change Password',
    'send_login_link': 'Send Login Link'
}

def get_form_field_label(key):
    return _default_field_labels.get(key, '')

class ExtLoginForm(LoginForm):
    email = StringField(get_form_field_label('email'), validators=[email_required, email_validator])
    password = PasswordField(get_form_field_label('password'), validators=[password_required])
    remember = BooleanField(get_form_field_label('remember_me'))
    submit = SubmitField(get_form_field_label('login'))

class ExtRegisterForm(RegisterForm):
    email = StringField(get_form_field_label('email'), validators=[email_required, email_validator, unique_user_email])
    password = PasswordField(get_form_field_label('password'), validators=[password_required])
    password_confirm = PasswordField(get_form_field_label('retype_password'), validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH')])
    submit = SubmitField(get_form_field_label('login'))