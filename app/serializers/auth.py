from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("email") or attrs.get("username")
        if not identifier:
            raise self.fail("no_active_account")
        attrs["username"] = identifier  # SimpleJWT espera 'username'

        data = super().validate(attrs)
        # 👇 añadimos el rol al response
        data["rol"] = self.user.rol
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol  # 👈 esto mete el rol dentro del JWT
        return token

