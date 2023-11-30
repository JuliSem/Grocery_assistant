import re

from rest_framework.validators import ValidationError


def validate_name_recipe(value):
    """Валидация данных в поле name рецепта."""
    if re.match(r'^[\d\W]+$', value):
        raise ValidationError('Название рецепта не должно состоять '
                              'только из цифр и знаков!')


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
