from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "city",
            "avatar",
            "telegram_chat_id",
            "telegram_username",
            "telegram_notifications",
            "role",
            "manager",
            "date_joined",
            "is_active",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False, # Обязательный пароль, в данном случае не нужен так как авторизация через телеграм
            },  # Пароль не будет отображаться в API
            "telegram_chat_id": {"read_only": True},  # Только для чтения
        }


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "phone_number",
            "city",
            "email",
            "avatar",
            "date_joined",
        ]
        read_only_fields = fields


class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "city",
            "email",
            "avatar",
            "date_joined",
            "payments",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "telegram_chat_id"
        ]


# В данном случае не нужно так как пользователь создается при первом запросе через телеграм бота
# class TelegramConnectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["telegram_chat_id"]
#         extra_kwargs = {"telegram_chat_id": {"required": True}}
