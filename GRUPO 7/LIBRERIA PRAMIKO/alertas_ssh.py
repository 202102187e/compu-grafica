import paramiko
import os


def menu_interactivo():
    """Muestra el menú en consola y captura la opción del usuario."""
    print("=" * 40)
    print("          MENÚ DE CONTROL SSH          ")
    print("=" * 40)
    print("1. Ejecutar comando de prueba ('whoami')")
    print("2. Enviar archivo de alerta por SFTP")
    print("3. Salir")
    print("=" * 40)
    return input("Selecciona una opción (1-3): ").strip()

# CONFIGURACIÓN DE LA CONEXIÓN
HOST = "localhost" 
USUARIO = "HERBSYSTEM"

print(f"--- Conectando a {HOST} vía SSH usando Llave Pública ---")

# Inicializar cliente SSH
cliente = paramiko.SSHClient()
cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Ruta automática hacia tu llave privada Ed25519 corregida
    ruta_llave = os.path.expanduser("~/.ssh/id_ed25519")
    llave_privada = paramiko.Ed25519Key.from_private_key_file(ruta_llave)

    # Conectarse usando la llave en lugar de password
    cliente.connect(hostname=HOST, username=USUARIO, pkey=llave_privada)
    print("¡Conexión SSH Establecida con éxito!\n")
    
    while True:
        opcion = menu_interactivo()

        if opcion == "1":
            print("\n[Ejecutando comando remoto por SSH...]")
            # 'whoami' muestra el usuario activo en el servidor OpenSSH
            comando = "whoami" 
            entrada, salida, errores = cliente.exec_command(comando)
            
            resultado = salida.read().decode('utf-8')
            error_res = errores.read().decode('utf-8')

            if resultado:
                print(f"\nRespuesta del Servidor:\n{resultado}")
            if error_res:
                print(f"\nError detectado:\n{error_res}")

        elif opcion == "2":
            print("\n[Abriendo canal SFTP para transferencia...]")
            mensaje = input("Escribe el mensaje de alerta para el servidor: ")
            
            # Crear un archivo de texto local temporal con el mensaje
            nombre_archivo = "alerta_remota.txt"
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write(f"ALERTA DEL SISTEMA:\n{mensaje}\n")

            # Conectarse por SFTP y subirlo a la carpeta del servidor
            sftp = cliente.open_sftp()
            # Lo sube directamente al escritorio del usuario en localhost
            ruta_remota = f"C:/Users/{USUARIO}/Desktop/{nombre_archivo}"
            sftp.put(nombre_archivo, ruta_remota)
            sftp.close()
            
            print(f"\n¡Éxito! El archivo fue depositado en el Escritorio del servidor.")

        elif opcion == "3":
            print("\nCerrando sesión interactiva...")
            break
        else:
            print("\nOpción no válida. Intenta de nuevo.\n")

except paramiko.AuthenticationException:
    print("\n[ERROR] Credenciales incorrectas o llave rechazada por el servidor.")
    print("Asegúrate de que el contenido de 'id_ed25519.pub' esté dentro de 'authorized_keys'.")
except Exception as e:
    print(f"\n[ERROR] No se pudo conectar: {e}")
finally:
    cliente.close()
    print("Conexión SSH finalizada de forma segura.")