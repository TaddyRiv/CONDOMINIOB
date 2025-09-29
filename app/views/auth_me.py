from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


#from rest_framework.decorators import api_view, permission_classes
#from app.serializers.usuario import UsuarioProfileSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        data = {
            "id": u.id,
            "username": getattr(u, "username", ""),
            "email": getattr(u, "email", ""),
            # ajusta a tu modelo si tienes campos/roles extra:
            "roles": getattr(u, "rol", ""),
            "nombre_completo": f"{u.first_name} {u.last_name}".strip(),
        }
        return Response(data)


##@api_view(["GET"])
##@permission_classes([IsAuthenticated])
##def me_view(request):
 ##   serializer = UsuarioProfileSerializer(request.user)
   ## return Response(serializer.data)
