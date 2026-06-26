from pathlib import Path

import pandas as pd

from src.utils.logger import Logger
from src.utils.performance import PerformanceMonitor, memoria_df


def cargar_csv(ruta: str, logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Cargador")
    log.paso("CSV", f"Leyendo {ruta}")
    df = pd.read_csv(ruta)
    log.ok("CSV", f"{len(df):,} filas x {len(df.columns)} columnas, {memoria_df(df)} MB")
    return df


def cargar_parquet(ruta: str, logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Cargador")
    log.paso("Parquet", f"Leyendo {ruta}")
    df = pd.read_parquet(ruta)
    log.ok("Parquet", f"{len(df):,} filas x {len(df.columns)} columnas, {memoria_df(df)} MB")
    return df


def cargar_json(ruta: str, logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Cargador")
    log.paso("JSON", f"Leyendo {ruta}")
    df = pd.read_json(ruta, lines=True)
    log.ok("JSON", f"{len(df):,} filas x {len(df.columns)} columnas, {memoria_df(df)} MB")
    return df


def cargar_dataset(ruta: str, logger: Logger | None = None, perf: PerformanceMonitor | None = None) -> pd.DataFrame:
    log = logger or Logger("Cargador")
    timer = perf or PerformanceMonitor()
    timer.iniciar()

    extension = Path(ruta).suffix.lower()
    log.paso("Dataset", f"Extension detectada: {extension}")

    loaders = {
        ".csv": cargar_csv,
        ".json": cargar_json,
        ".parquet": cargar_parquet,
    }

    if extension not in loaders:
        log.error("Dataset", f"Formato no soportado: {extension}")
        raise ValueError(f"Formato de archivo no soportado: {extension}")

    df = loaders[extension](ruta, logger=log)
    timer.marcar("carga")
    log.ok("Dataset", f"Archivo cargado: {len(df):,} filas, {memoria_df(df)} MB")
    if not perf:
        timer.imprimir_reporte()

    return df