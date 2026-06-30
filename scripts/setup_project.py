import os
import shutil
import subprocess
import sys

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(root_dir, "template")
    admin_dir = os.path.join(root_dir, "admin")
    backend_dir = os.path.join(root_dir, "backend")

    print("=== Iniciando Configuración del Expediente Clínico ZOE ===")

    # 1. Copiar plantilla a admin
    if not os.path.exists(template_dir):
        print(f"ERROR: La carpeta template no existe en {template_dir}")
        sys.exit(1)

    print(f"Copiando plantilla de {template_dir} a {admin_dir}...")
    if os.path.exists(admin_dir):
        print("La carpeta admin ya existe. Realizando copia incremental...")
        # Copiar archivos incrementales
        for root, dirs, files in os.walk(template_dir):
            rel_path = os.path.relpath(root, template_dir)
            target_path = os.path.join(admin_dir, rel_path)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_path, file)
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
    else:
        shutil.copytree(template_dir, admin_dir)
    print("Plantilla copiada exitosamente.")

    # 2. Configurar backend venv
    venv_dir = os.path.join(backend_dir, "venv")
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    print(f"Configurando entorno virtual en {venv_dir}...")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Entorno virtual creado.")
    else:
        print("El entorno virtual ya existe.")

    # Determinar el binario de python del venv
    python_path = os.path.join(venv_dir, "Scripts", "python.exe")
    if not os.path.exists(python_path):
        python_path = os.path.join(venv_dir, "bin", "python")

    if os.path.exists(requirements_file):
        print("Instalando dependencias de Python...")
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([python_path, "-m", "pip", "install", "-r", requirements_file], check=True)
        print("Dependencias de Python instaladas.")
    else:
        print("ADVERTENCIA: No se encontró requirements.txt en backend/.")

    # 3. Instalar dependencias del frontend (npm install)
    print("Instalando dependencias de Node.js (admin)...")
    try:
        # Usar shell=True para Windows
        subprocess.run(["npm", "install"], cwd=admin_dir, shell=True, check=True)
        print("Dependencias de Node.js instaladas exitosamente.")
    except Exception as e:
        print(f"ERROR al instalar dependencias de Node.js: {e}")
        print("Por favor, asegúrate de tener Node.js instalado y corre 'npm install' manualmente dentro de la carpeta admin/.")

    print("\n=== Configuración Inicial Completada con Éxito ===")

if __name__ == "__main__":
    main()
