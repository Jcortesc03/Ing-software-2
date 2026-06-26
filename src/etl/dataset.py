import kagglehub
import shutil
from pathlib import Path

# Descargar al caché
cache_path = Path(kagglehub.dataset_download("shivamparab/amazon-electronics-reviews"))

# Carpeta destino dentro del proyecto
project_path = Path("./data/raw")
    
# Crear la carpeta si no existe
project_path.mkdir(parents=True, exist_ok=True)

# Copiar todos los archivos
for file in cache_path.iterdir():
    if file.is_file():
        shutil.copy(file, project_path / file.name)

# Eliminar la carpeta del caché
shutil.rmtree(cache_path)

print(f"Dataset copiado a: {project_path.resolve()}")