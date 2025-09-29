from django.contrib.auth import get_user_model

def run():
    Usuario = get_user_model()
    # Crear superusuario administrador
    if not Usuario.objects.filter(username="admin").exists():
        Usuario.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
            rol="ADMIN",
            ci="12345678"
        )
        print("✅ Usuario admin creado")
    else:
        print("⚠️ Usuario admin ya existe")



    # Crear usuario residente 1
    if not Usuario.objects.filter(username="residente1").exists():
        Usuario.objects.create_user(
            username="residente1",
            email="residente1@example.com",
            password="res1234",
            rol="RESIDENTE",
            ci="87654321"
        )
        print("✅ Usuario residente creado")
    else:
        print("⚠️ Usuario residente ya existe")

    # Crear usuario guardia de seguridad
    if not Usuario.objects.filter(username="guardia1").exists():
        Usuario.objects.create_user(
            username="guardia1",
            email="guardia1@example.com",
            password="guard1234",
            rol="GUARDIA",
            ci="11223344"
        )
        print("✅ Usuario guardia creado")
    else:
        print("⚠️ Usuario guardia ya existe")
