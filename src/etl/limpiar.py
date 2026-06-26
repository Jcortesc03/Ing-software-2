import pandas as pd

from src.utils.logger import Logger
from src.utils.performance import PerformanceMonitor, memoria_df


def eliminar_duplicados(df: pd.DataFrame, subset: list | None = None,
                        logger: Logger | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    log.paso("Duplicados", "Eliminando filas duplicadas")
    filas_antes = len(df)
    if subset is None:
        subset = [col for col in df.columns if not _tiene_tipo_no_hashable(df[col])]
    df_limpio = df.drop_duplicates(subset=subset)
    filas_eliminadas = filas_antes - len(df_limpio)
    log.ok("Duplicados", f"{filas_eliminadas:,} filas eliminadas, {len(df_limpio):,} restantes")
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def _tiene_tipo_no_hashable(col: pd.Series) -> bool:
    if col.dtype != "object":
        return False
    primer_valor = col.dropna().iloc[0] if not col.dropna().empty else None
    return isinstance(primer_valor, list)


def eliminar_nulos(df: pd.DataFrame, subset: list | None = None,
                   logger: Logger | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    log.paso("Nulos", "Eliminando filas con valores nulos")
    filas_antes = len(df)
    df_limpio = df.dropna(subset=subset)
    filas_eliminadas = filas_antes - len(df_limpio)
    log.ok("Nulos", f"{filas_eliminadas:,} filas eliminadas, {len(df_limpio):,} restantes")
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def eliminar_reviews_vacias(df: pd.DataFrame,
                            logger: Logger | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    log.paso("Reviews", "Eliminando reviews vacias")
    filas_antes = len(df)
    mask = df["reviewText"].notna() & (df["reviewText"].str.strip() != "")
    df_limpio = df[mask].copy()
    filas_eliminadas = filas_antes - len(df_limpio)
    log.ok("Reviews", f"{filas_eliminadas:,} filas eliminadas, {len(df_limpio):,} restantes")
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def eliminar_rating_invalidos(df: pd.DataFrame, min_val: int = 1, max_val: int = 5,
                              logger: Logger | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    log.paso("Rating", f"Filtrando ratings fuera de rango [{min_val}, {max_val}]")
    filas_antes = len(df)
    df_limpio = df[df["overall"].between(min_val, max_val)].copy()
    filas_eliminadas = filas_antes - len(df_limpio)
    log.ok("Rating", f"{filas_eliminadas:,} filas eliminadas, {len(df_limpio):,} restantes")
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def limpiar_espacios(df: pd.DataFrame, columnas: list | None = None,
                     logger: Logger | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    log.paso("Espacios", "Limpiando espacios en blanco")
    cols = columnas if columnas else [col for col in df.columns if _es_columna_string(df[col])]
    total_modificadas = 0
    for col in cols:
        if col in df.columns:
            antes = df[col].str.strip() != df[col]
            df[col] = df[col].str.strip()
            total_modificadas += antes.sum()
    log.ok("Espacios", f"{total_modificadas:,} celdas modificadas")
    return df, {"celdas_modificadas": int(total_modificadas)}


def _es_columna_string(col: pd.Series) -> bool:
    if pd.api.types.is_string_dtype(col):
        return True
    if col.dtype != "object":
        return False
    primer_valor = col.dropna().iloc[0] if not col.dropna().empty else None
    return isinstance(primer_valor, str)


def limpiar_dataset(df: pd.DataFrame, logger: Logger | None = None,
                    perf: PerformanceMonitor | None = None) -> tuple[pd.DataFrame, dict]:
    log = logger or Logger("Limpiador")
    timer = perf or PerformanceMonitor()
    timer.iniciar()

    log.divider()
    log.paso("Dataset", f"Iniciando limpieza - {len(df):,} filas, {memoria_df(df)} MB")
    resultados = {}

    df, r = eliminar_duplicados(df, logger=log)
    resultados["duplicados"] = r
    timer.marcar("duplicados")

    df, r = eliminar_nulos(df, logger=log)
    resultados["nulos"] = r
    timer.marcar("nulos")

    if "reviewText" in df.columns:
        df, r = eliminar_reviews_vacias(df, logger=log)
        resultados["reviews_vacias"] = r
    else:
        resultados["reviews_vacias"] = {"filas_eliminadas": 0}
    timer.marcar("reviews_vacias")

    if "overall" in df.columns:
        df, r = eliminar_rating_invalidos(df, logger=log)
        resultados["rating_invalidos"] = r
    else:
        resultados["rating_invalidos"] = {"filas_eliminadas": 0}
    timer.marcar("rating_invalidos")

    df, r = limpiar_espacios(df, logger=log)
    resultados["espacios"] = r
    timer.marcar("espacios")

    log.ok("Dataset", f"Limpieza completada - {len(df):,} filas, {memoria_df(df)} MB")
    log.divider()

    if not perf:
        timer.imprimir_reporte()
        log.divider()

    return df, resultados
