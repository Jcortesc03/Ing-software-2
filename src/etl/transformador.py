import re
from pathlib import Path

import pandas as pd

from src.utils.logger import Logger
from src.utils.performance import PerformanceMonitor, memoria_df


def convertir_tipos(df: pd.DataFrame, esquema: dict | None = None,
                    logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Transformador")
    log.paso("Tipos", "Convirtiendo tipos de datos")
    df = df.copy()

    if esquema:
        for col, tipo in esquema.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(tipo)
                    log.info(f"  {col}: convertido a {tipo}")
                except (ValueError, TypeError) as e:
                    log.warning("Tipos", f"No se pudo convertir {col} a {tipo}: {e}")

    log.ok("Tipos", "Conversion de tipos finalizada")
    return df


def transformar_fechas(df: pd.DataFrame,
                       logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Transformador")
    log.paso("Fechas", "Transformando columnas de fecha")
    df = df.copy()

    if "unixReviewTime" in df.columns:
        df["fecha_review"] = pd.to_datetime(df["unixReviewTime"], unit="s")
        df["anio_review"] = df["fecha_review"].dt.year.astype("int32")
        df["mes_review"] = df["fecha_review"].dt.month.astype("int32")
        df["dia_review"] = df["fecha_review"].dt.day.astype("int32")
        df["dia_semana"] = df["fecha_review"].dt.dayofweek.astype("int32")
        log.info(f"  Creadas: fecha_review, anio_review, mes_review, dia_review, dia_semana")

    if "reviewTime" in df.columns:
        df["fecha_original"] = pd.to_datetime(df["reviewTime"], format="%m %d, %Y", errors="coerce")
        log.info("  Normalizado reviewTime a fecha_original")

    log.ok("Fechas", "Transformacion de fechas completada")
    return df


def crear_variables(df: pd.DataFrame,
                    logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Transformador")
    log.paso("Variables", "Creando nuevas variables")
    df = df.copy()

    if "helpful" in df.columns:
        df["votos_utiles"] = df["helpful"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 0).astype("int32")
        df["votos_totales"] = df["helpful"].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else 0).astype("int32")
        df["tasa_utilidad"] = (
            df["votos_utiles"] / df["votos_totales"].replace(0, float("nan"))
        ).round(4)
        log.info("  Creadas: votos_utiles, votos_totales, tasa_utilidad")

    if "overall" in df.columns:
        condiciones = [
            df["overall"] >= 4,
            df["overall"] == 3,
        ]
        valores = ["positivo", "neutro", "negativo"]
        df["sentimiento"] = pd.cut(
            df["overall"], bins=[0, 2, 3, 5], labels=["negativo", "neutro", "positivo"],
            right=True, include_lowest=True,
        ).astype(str)
        log.info("  Creada: sentimiento (positivo/neutro/negativo)")

    if "reviewText" in df.columns:
        df["longitud_review"] = df["reviewText"].str.len().astype("int32")
        df["cantidad_palabras"] = df["reviewText"].str.split().str.len().astype("int32")
        log.info("  Creadas: longitud_review, cantidad_palabras")

    if "summary" in df.columns:
        df["longitud_summary"] = df["summary"].str.len().astype("int32")
        log.info("  Creada: longitud_summary")

    log.ok("Variables", f"Total columnas: {len(df.columns)}")
    return df


def normalizar_texto(df: pd.DataFrame, columnas: list | None = None,
                     logger: Logger | None = None) -> pd.DataFrame:
    log = logger or Logger("Transformador")
    df = df.copy()

    cols = columnas if columnas else [col for col in df.columns if pd.api.types.is_string_dtype(df[col])]
    log.paso("Texto", f"Normalizando texto en {len(cols)} columna(s)")

    for col in cols:
        if col not in df.columns:
            continue
        df[col] = df[col].str.lower().str.strip()
        df[col] = df[col].apply(lambda x: re.sub(r"\s+", " ", x) if pd.notna(x) else x)
        log.info(f"  Normalizado: {col}")

    log.ok("Texto", "Normalizacion de texto completada")
    return df


def guardar_parquet(df: pd.DataFrame, nombre: str,
                    logger: Logger | None = None) -> str:
    log = logger or Logger("Transformador")
    ruta = Path("data") / "processed" / f"{nombre}.parquet"
    ruta.parent.mkdir(parents=True, exist_ok=True)

    log.paso("Parquet", f"Guardando en {ruta}")
    df.to_parquet(ruta, index=False)
    tam_mb = ruta.stat().st_size / 1024**2
    log.ok("Parquet", f"Archivo guardado: {tam_mb:.2f} MB, {len(df):,} filas")
    return str(ruta)


def transformar_dataset(df: pd.DataFrame, nombre_salida: str = "electronics_processed",
                        esquema_tipos: dict | None = None,
                        logger: Logger | None = None,
                        perf: PerformanceMonitor | None = None) -> tuple[pd.DataFrame, str, dict]:
    log = logger or Logger("Transformador")
    timer = perf or PerformanceMonitor()
    timer.iniciar()

    log.divider()
    log.paso("Dataset", f"Iniciando transformacion - {len(df):,} filas, {memoria_df(df)} MB")
    resultados = {}

    df = convertir_tipos(df, esquema=esquema_tipos, logger=log)
    timer.marcar("convertir_tipos")
    resultados["convertir_tipos"] = df.shape

    df = transformar_fechas(df, logger=log)
    timer.marcar("fechas")
    resultados["fechas"] = df.shape

    df = crear_variables(df, logger=log)
    timer.marcar("variables")
    resultados["variables"] = df.shape

    df = normalizar_texto(df, logger=log)
    timer.marcar("texto")
    resultados["texto"] = df.shape

    ruta = guardar_parquet(df, nombre_salida, logger=log)
    timer.marcar("parquet")
    resultados["parquet"] = ruta
    resultados["memoria_final_mb"] = memoria_df(df)

    log.ok("Dataset", f"Transformacion completada - {len(df):,} filas x {len(df.columns)} columnas, {memoria_df(df)} MB")
    log.info(f"  Archivo: {ruta}")
    log.divider()

    if not perf:
        timer.imprimir_reporte()
        log.divider()

    return df, ruta, resultados
