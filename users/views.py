from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.paginators import MyPagination
from users.models import CustomUser
from users.permissions import IsOwnerOrAdmin, IsProfileOwner
from users.serializers import (CustomUserSerializer, PrivateUserSerializer,
                               PublicUserSerializer)
from django.contrib.auth import get_user_model


# POST
class CustomUserCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny] # В данном случае доступ пока у всех так как бот Аноним

    def perform_create(self, serializer):
        password = serializer.validated_data.get("password")
        user = serializer.save(is_active=True)
        user.set_password(password)
        user.save()


# PATCH
class CustomUserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = "email"
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


# DELETE
class CustomUserDeleteAPIView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = "email"
    permission_classes = [IsAuthenticated, IsAdminUser]


# GET
class CustomUserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    pagination_class = MyPagination
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminUser]


# GET
class CustomUserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    #queryset = CustomUser.objects.all() - указываем с какой моделью работать,
    lookup_field = "email"
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        # Только активные пользователи
        return CustomUser.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return PrivateUserSerializer
        return PublicUserSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsProfileOwner()]


# GET
class ManagerExecutorsListView(generics.ListAPIView):
    """Список исполнителей текущего менеджера"""
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()

    def get_queryset(self):
        # Получаем текущего пользователя
        user = self.request.user

        # Проверяем что пользователь - менеджер
        if user.role != 'manager':
            return CustomUser.objects.none()  # ✅ Используй CustomUser

        return CustomUser.objects.filter(manager=user, role='executor')


# В данном случае не нужно так как пользователь создается при первом запросе через телеграм бота
# class ConnectTelegramView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def patch(self, request):
#         serializer = TelegramConnectSerializer(
#             instance=request.user,   # Какой пользователь обновляется
#             data=request.data,       # Данные от клиента (telegram_chat_id)
#             partial=True             # Разрешить частичное обновление
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"status": "Telegram chat ID успешно сохранен"},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
