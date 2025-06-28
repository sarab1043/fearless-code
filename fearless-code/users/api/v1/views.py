import os
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from authentication.models import Language
from superadmin.models import Resources
from users.models import ChatMessage, ChatRoom
from users.serializers import LanguageSerializer, ResourceSerializer, RoomMessagesSerializer, RoomsSerializer
from utils.constants import *
from utils.pagination import CustomPagination
from utils.utils import *

from utils.agent2 import PhiResponder

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import logging
from rest_framework.pagination import LimitOffsetPagination
from django.template.loader import render_to_string
from weasyprint import HTML
logger = logging.getLogger(__name__)

from datetime import datetime

current_year = datetime.now().year

import random

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Invalid login details.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'token': token.key
        })

# Current chat 
class ChatRoomsApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
 
    # create new room
    def post(self, request):
        try:
            user = request.user
            chat_count = ChatRoom.objects.filter(user=user).count()
            room_name = f"Chat No {chat_count + 1}"
            
            room_type = request.data.get("type", "advisior")

            # create room
            room = ChatRoom.objects.create(user=user, name=room_name, type=room_type)
            serializer = RoomsSerializer(room, context={'request': request})
    
            return Response({
                SUCCESS: TRUE,
                MESSAGE:ROOMS_CREATED_SUCCESS,
                DATA :serializer.data
            }, status=status.HTTP_200_OK)

        except ChatRoom.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: ROOMS_NOT_CREATED},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        except Exception as ex:
            logger.exception("Error processing chat request.")
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_CREATED, ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)
        
    # update current open chat rooom
    def put(self, request):
        try:
            user = request.user
            room_uuid = request.query_params.get("room_uuid")
            name = request.data.get("name")
            is_saved = request.data.get("is_saved")
            
            if not room_uuid:
                return Response({ SUCCESS: FALSE, ERROR: "'room_uuid' is required." }, status=status.HTTP_404_NOT_FOUND)
            
            # create room
            room = ChatRoom.objects.filter(user=user, uuid=room_uuid).first()
            if not room:
                return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            # Update room name
            if name is not None:
                room.name = name
            if is_saved is not None:
                room.is_saved = is_saved
            room.save()
            
            serializer = RoomsSerializer(room, context={'request': request})
    
            return Response({
                SUCCESS: TRUE,
                MESSAGE:ROOMS_UPDATED_SUCCESS,
                DATA :serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as ex:
            logger.exception("Error processing chat request.")
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_UPDATED, ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)
        
    # delete current open chat 
    def delete(self, request):
        try:
            user = request.user
            room_uuid = request.query_params.get("room_uuid")

            if not room_uuid:
                return Response({SUCCESS: FALSE, ERROR: "Room UUID is required."}, status=status.HTTP_404_NOT_FOUND)

            room = ChatRoom.objects.filter(user=user, uuid=room_uuid).first()
            if not room:
                return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            room.delete()
            return Response({SUCCESS: TRUE, MESSAGE: ROOMS_DELETED_SUCCESS}, status=status.HTTP_200_OK)

        except Exception as ex:
            logger.exception("Error deleting chat room.")
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_DELETED, ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)
        
# current chat messages 


agent = PhiResponder()
class AdvisorChatMessagesApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid=None):
        try:
            room_uuid = uuid
            user_prompt = request.data.get('prompt', '')

            # user_prompt = request.query_params.get('prompt', '')

            user = request.user
            if not user_prompt:
                return Response({SUCCESS: FALSE, ERROR: "The 'prompt' field is required."}, status=status.HTTP_404_NOT_FOUND)
            

            room = ChatRoom.objects.get(user=user, uuid=room_uuid)
            ChatMessage.objects.create(room=room,user=user,prompt=user_prompt)
        

            previous_messages = ChatMessage.objects.filter(room=room).order_by("-created_at")[:3]
            messages = []           
            for msg in previous_messages[::-1]:
                if msg.prompt:
                    messages.append({"role": "user", "content": msg.prompt})
                if msg.response:
                    messages.append({"role": "assistant", "content": msg.response})


            try:
                response = agent.ask(messages, user_prompt, role="assistant")

            except Exception as ex:
                logger.exception("Error processing chat request.")
                return Response({SUCCESS: FALSE, ERROR: 'Error processing chat request.', ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)

            if response:
                messages = ChatMessage.objects.create(room=room,response=response)
                serializer = RoomMessagesSerializer(messages, context={'request': request})
            
            response_data = {
                SUCCESS: TRUE,
                "response": response.strip(),
                "room": serializer.data["room"],
                "created_at": serializer.data["created_at"],
                "updated_at": serializer.data["updated_at"],
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
            
        except ChatRoom.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            logger.exception("Error processing chat request.")
            return Response({SUCCESS: FALSE, ERROR: 'Error processing chat request.', ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)
            
    # all rooms listing
class RoomsApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    
    # get all rooms
    def get(self, request, *args, **kwargs):
        try:
            rooms = ChatRoom.objects.filter(user=request.user, is_saved=True).order_by('-created_at')
            paginator = self.pagination_class()
            paginated_rooms = paginator.paginate_queryset(rooms, request)
            serializer = RoomsSerializer(paginated_rooms, many=True, context={'request': request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: ROOMS_LIST_SUCESS,
                    COUNT:paginator.page.paginator.count,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ChatRoom.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception as ex:
            return Response({ SUCCESS:FALSE, ERROR: ROOMS_NOT_FOUND , ERROR_MESSAGE:str(ex) }, status=status.HTTP_404_NOT_FOUND)
        
     
        
# messages of room  
class RoomMessagesApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get(self, request, uuid=None):
        try:
            room_uuid = uuid
            user=request.user
            room = ChatRoom.objects.get(user=user, uuid=room_uuid)  
            messages = ChatMessage.objects.filter(room=room).order_by("-created_at")
            # paginator = LimitOffsetPagination()
            # paginator.default_limit = 20
            paginator = self.pagination_class()
            paginator_messages = paginator.paginate_queryset(messages, request)
            
            # show all messages limit=-1
            limit = request.query_params.get('limit')
            if limit == '-1':
                serializer = RoomMessagesSerializer(paginator_messages, many=True, context={'request': request})
                return Response(
                    {
                        SUCCESS: TRUE,
                        MESSAGE: MESSAGES_LIST_SUCESS,
                        COUNT: paginator.page.paginator.count,
                        DATA: serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            serializer = RoomMessagesSerializer(paginator_messages, many=True, context={'request': request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: MESSAGES_LIST_SUCESS,
                    # count': paginator.count  
                    COUNT: paginator.page.paginator.count,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ChatRoom.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, 'is_room':FALSE, 'is_messages':FALSE, ERROR: ROOMS_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        except ChatMessage.DoesNotExist:
            pass
            # return Response(
            #     {SUCCESS: FALSE, 'is_messages':FALSE, ERROR: MESSAGES_NOT_FOUND},
            #     status=status.HTTP_404_NOT_FOUND,
            # )
        
        except Exception as ex:
            return Response({ SUCCESS:FALSE, ERROR: MESSAGES_NOT_FOUND, ERROR_MESSAGE: str(ex) }, status=status.HTTP_404_NOT_FOUND)


#export pdf 
class ChatRoomPDFExportAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid=None):
        try:
            room_uuid = uuid
            user = request.user
            room = ChatRoom.objects.get(user=user, uuid=room_uuid)
            messages = ChatMessage.objects.filter(room=room).order_by('created_at')

            context = {
                'room': room,
                'messages': messages
            }

            html_string = render_to_string('pdf/export-pdf.html', context)
            pdf_file = HTML(string=html_string).write_pdf()

            pdf_folder = os.path.join(settings.MEDIA_ROOT, 'uploads/chat_pdfs')
            os.makedirs(pdf_folder, exist_ok=True)

            pdf_filename = f'chat_{room_uuid}.pdf'
            pdf_path = os.path.join(pdf_folder, pdf_filename)

            # already exists, delete it
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            # Save new PDF
            with open(pdf_path, 'wb') as f:
                f.write(pdf_file)

            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/chat_pdfs/' + pdf_filename)

            # Return PDF URL in JSON response
            return Response({
                SUCCESS: TRUE,
                "pdf_url": pdf_url
            }, status=status.HTTP_200_OK)

        except ChatRoom.DoesNotExist:
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND, ERROR_MESSAGE: str(ex)}, status=status.HTTP_404_NOT_FOUND)
        
        
class ResourcesListApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    
    def get(self, request, *args, **kwargs):
        try:
            resources = Resources.objects.all()
            paginator = self.pagination_class()
            paginated_resources = paginator.paginate_queryset(resources, request)
            serializer = ResourceSerializer(paginated_resources, many=True, context={'request': request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: RESOURCES_LIST_SUCESS,
                    COUNT: paginator.page.paginator.count,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Resources.DoesNotExist:
            return Response(
                {SUCCESS: FALSE, ERROR: RESOURCES_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception as ex:
            return Response({ SUCCESS:FALSE,  ERROR: RESOURCES_NOT_FOUND, ERROR_MESSAGE: str(ex) },status=status.HTTP_404_NOT_FOUND)
            
            
            
class LanguageListApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, *args, **kwargs):
        try:
            languages = Language.objects.all()
            serializer = LanguageSerializer(languages, many=True, context={'request': request})
            return Response(
                {
                    SUCCESS: TRUE,
                    MESSAGE: LANGUAGE_LIST_SUCESS,
                    DATA: serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Language.DoesNotExist:
            return Response({ SUCCESS: FALSE, ERROR: LANGUAGE_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as ex:
            return Response({ SUCCESS:FALSE, ERROR: LANGUAGE_NOT_FOUND, ERROR_MESSAGE: str(ex)}, status=status.HTTP_404_NOT_FOUND)
        


class AgentschatApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid=None):
        try:
            room_uuid = uuid
            user_prompt = request.data.get('prompt', '')
            # user_prompt = request.query_params.get("prompt")
            user = request.user
            if not user_prompt:
                return Response({SUCCESS: FALSE, ERROR: "The 'prompt' field is required."}, status=status.HTTP_404_NOT_FOUND)

            room = ChatRoom.objects.get(user=user, uuid=room_uuid)
            ChatMessage.objects.create(room=room, prompt=user_prompt)


            try:
                previous_messages = ChatMessage.objects.filter(room=room).order_by("-created_at")[:3]
                messages = []
                
                for msg in previous_messages[::-1]:
                    if msg.prompt:
                        messages.append({"role": "user", "content": msg.prompt})
                    if msg.response:
                        messages.append({"role": "assistant", "content": msg.response})
                try:
                    response = agent.ask(messages, user_prompt, role="wellness")
                except Exception as ex:
                    logger.exception("Error processing chat request.")
                    return Response({SUCCESS: FALSE, ERROR: 'Error processing chat request.', ERROR_MESSAGE:str(ex)}, status=status.HTTP_404_NOT_FOUND)
                
                # Validate response
                if not response:
                    return Response({
                        SUCCESS: FALSE,
                        ERROR: "No response generated"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                if "timed out" in response.lower():
                    return Response({
                        SUCCESS: FALSE,
                        ERROR: "Request timed out",
                        ERROR_MESSAGE: response
                    }, status=status.HTTP_504_GATEWAY_TIMEOUT)
                    
            except Exception as e:
                return Response({
                    SUCCESS: FALSE,
                    ERROR: "Error processing request",
                    ERROR_MESSAGE: str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                # Create message and serialize
                messages = ChatMessage.objects.create(room=room, response=response)
                serializer = RoomMessagesSerializer(messages, context={'request': request})
                
                return Response({
                    SUCCESS: TRUE,
                    "response": response.strip(),
                    "room": serializer.data["room"],
                    "created_at": serializer.data["created_at"],
                    "updated_at": serializer.data["updated_at"],
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                # Log the specific error
                logger.error(f"Error creating chat message: {str(e)}")
                return Response({
                    SUCCESS: FALSE,
                    ERROR: "Error saving chat message",
                    ERROR_MESSAGE: str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ChatRoom.DoesNotExist:
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({SUCCESS: FALSE, ERROR: 'Error processing chat request.', ERROR_MESSAGE: str(ex)}, status=status.HTTP_404_NOT_FOUND)



fearless_questions = {
    "What are you noticing in your thinking right now?": [
        "What patterns are you observing in your thoughts today?",
        "What kind of thinking is most active for you right now?",
        "Where is your attention naturally going in this moment?",
    ],
    "How are you responding when fear or doubt shows up?": [
        "What tends to happen when uncertainty enters your mind?",
        "How do your actions shift when fear surfaces?",
        "What’s your usual response when doubt arises?",
    ],
    "Where are you acting automatically instead of consciously?": [
        "What part of your day feels like it runs on autopilot?",
        "Where are your thoughts leading without your full attention?",
        "What do you notice about unconscious patterns in how you act?",
    ],
    "What happens right after you say 'I can’t'?": [
        "What usually follows the thought 'I can’t'?",
        "What shows up in behavior or energy after that phrase?",
        "How do you act once you’ve told yourself something isn’t possible?",
    ],
    "How do you engage with challenges when they first arise?": [
        "What’s your first internal move when a problem appears?",
        "How do you typically respond the moment something feels difficult?",
        "What immediate thought or emotion arises with challenge?",
    ],
    "What signals show up when your thinking is off-track?": [
        "What inner alarms go off when your thoughts shift negatively?",
        "How does your body or emotion reflect misaligned thinking?",
        "What cues tell you it’s time to examine your thoughts?",
    ],
    "What have you accepted that no longer serves you?": [
        "Where are you tolerating something that feels off?",
        "What are you putting up with that drains your energy?",
        "What feels stuck that you haven't yet questioned?",
    ],
    "How does clarity change how you act?": [
        "What do you notice about your behavior when you're clear?",
        "How do decisions shift when your mind is settled?",
        "What becomes possible once your thinking sharpens?",
    ]
}

def get_random_fearless_questions(n=3):
    selected = random.sample(list(fearless_questions.items()), k=n)
    return [random.choice(rephrasings) for _, rephrasings in selected]



class RandomQuestionApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
        
            questions = get_random_fearless_questions() 

            return Response({
                SUCCESS: TRUE,
                "questions": [questions[0], questions[1], questions[2]]
            }, status=status.HTTP_200_OK)

        except ChatRoom.DoesNotExist:
            return Response({SUCCESS: FALSE, ERROR: ROOMS_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({SUCCESS: FALSE, ERROR: 'Error processing chat request.', ERROR_MESSAGE: str(ex)}, status=status.HTTP_404_NOT_FOUND)
        