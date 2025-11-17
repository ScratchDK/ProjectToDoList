from rest_framework import permissions


class AuthTelegramJWT(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
