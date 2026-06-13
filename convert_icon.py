from PIL import Image
import os

# Rutas
png_path = r"C:\Users\Usuario\.gemini\antigravity\brain\5ebcdf20-1b7a-4dfd-b00f-921af2090341\facturas_app_icon_1770268213663.png"
ico_path = r"c:\Users\Usuario\Desktop\Facturas_GanaTodo_v4\assets\app.ico"

# Asegurar que existe el directorio
os.makedirs(os.path.dirname(ico_path), exist_ok=True)

# Convertir PNG a ICO con múltiples tamaños
img = Image.open(png_path)

# Redimensionar a cuadrado si no lo es
if img.size[0] != img.size[1]:
    # Tomar el lado más pequeño
    size = min(img.size)
    img = img.crop((0, 0, size, size))

# Crear íconos en múltiples tamaños (Windows recomienda estos)
icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img.save(ico_path, format='ICO', sizes=icon_sizes)

print(f"✅ Ícono creado exitosamente: {ico_path}")
print(f"   Tamaños incluidos: {icon_sizes}")
