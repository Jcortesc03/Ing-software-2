from pathlib import Path
import pandas as pd


def cargar_csv(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ruta)


def cargar_parquet(ruta: str) -> pd.DataFrame:
    return pd.read_parquet(ruta)


def cargar_json(ruta: str) -> pd.DataFrame:
    return pd.read_json(ruta, lines=True)


def cargar_dataset(ruta: str) -> pd.DataFrame:
    extension = Path(ruta).suffix.lower()

    loaders = {
        ".csv": cargar_csv,
        ".json": cargar_json,
        ".parquet": cargar_parquet,
    }

    if extension not in loaders:
        raise ValueError(f"Formato de archivo no soportado: {extension}")

    return loaders[extension](ruta)