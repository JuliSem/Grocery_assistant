import re

from rest_framework.validators import ValidationError


def validate_username(value):
    """Валидация данных в поле username."""
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError('Имя пользователя содержит запрещённые символы!'
                              'Допустимы: любые буквы(от "a" до "z" '
                              'и от "A" до "Z"), цифры от 0 до 9, а также '
                              'знаки: "_", ".", "@", "+", "-".')


def validate_tag_slug(value):
    """Валидация данных в поле slug Тега."""
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError('Поле slug тега содержит запрещённые символы!'
                              'Допустимы: любые буквы(от "a" до "z" '
                              'и от "A" до "Z"), цифры от 0 до 9, а также '
                              'знак "_".')


def validate_tag_color(value):
    """Валидация данных в поле color Тега."""
    if not re.match(r'^#([A-Fa-f0-9]{6})$', value):
        raise ValidationError('Поле color тега содержит запрещённые символы!'
                              'Цвет должен начинаться со знака "#" '
                              'и содержать 6 символов: допустимы: любые буквы'
                              '(от "a" до "f" и от "A" до "F"),'
                              'цифры от 0 до 9.')
