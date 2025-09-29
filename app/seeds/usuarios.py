from django.contrib.auth import get_user_model

def run():
     Usuario = get_user_model()
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
        
         ## borre usuarios
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

     if not Usuario.objects.filter(username="residente100").exists():
        Usuario.objects.create_user(
            username="residente100",
            email="residente100@example.com",
            password="123",
            rol="RESIDENTE",
            ci="345345678987667"
        )
        print("✅ Usuario residente creado")
     else:
        print("⚠ Usuario residente ya existe")


