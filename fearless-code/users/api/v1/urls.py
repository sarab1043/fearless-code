from django.urls import path
from users.api.v1 import views




urlpatterns = [
    path("auth/login", views.LoginAPIView.as_view(), name="login"),
    path("chat/room",views.ChatRoomsApiView.as_view(), name="chat-rooms"),
    path("chat/message/<uuid:uuid>", views.AdvisorChatMessagesApiView.as_view(), name="chat-messages"),
    path("rooms", views.RoomsApiView.as_view(), name="rooms"),
    path("room/messages/<uuid:uuid>", views.RoomMessagesApiView.as_view(), name="room-messages"),
    path("room/messages/<uuid:uuid>/export-pdf", views.ChatRoomPDFExportAPIView.as_view(), name="export-pdf-messages"),
    path("languages", views.LanguageListApiView.as_view(), name="languages"),
    path('resources', views.ResourcesListApiView.as_view(), name="resources-list"),
    path('agents/chat/message/<uuid:uuid>', views.AgentschatApiView.as_view(), name="agents-chat-messages"),
    path("chat/random-questions", views.RandomQuestionApiView.as_view(), name="random-questions"),
]
