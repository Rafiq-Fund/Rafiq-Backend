from django.conf import settings
import jwt
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from account.models import User
from account.utiles import send_activation_email
from account.serializers import RegisterSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user, self.request)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    


@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class ActivateAccountView(APIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "activation":
                return Response({"error": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)
            if user.verified:
                return Response({"detail": "Account already activated"}, status=status.HTTP_200_OK)
            
            user.verified = True
            user.save()
            return Response({"detail": "Account activated successfully"}, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError:
            return Response({"error": "Activation link expired"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    

