import pandas as pd


def eliminar_duplicados(df: pd.DataFrame, subset: list | None = None) -> tuple[pd.DataFrame, dict]:
    filas_antes = len(df)
    if subset is None:
        subset = [col for col in df.columns if not _tiene_tipo_no_hashable(df[col])]
    df_limpio = df.drop_duplicates(subset=subset)
    filas_eliminadas = filas_antes - len(df_limpio)
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def _tiene_tipo_no_hashable(col: pd.Series) -> bool:
    if col.dtype != "object":
        return False
    primer_valor = col.dropna().iloc[0] if not col.dropna().empty else None
    return isinstance(primer_valor, list)


def eliminar_nulos(df: pd.DataFrame, subset: list | None = None) -> tuple[pd.DataFrame, dict]:
    filas_antes = len(df)
    df_limpio = df.dropna(subset=subset)
    filas_eliminadas = filas_antes - len(df_limpio)
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def eliminar_reviews_vacias(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    filas_antes = len(df)
    mask = df["reviewText"].str.strip() != ""
    df_limpio = df[mask].copy()
    filas_eliminadas = filas_antes - len(df_limpio)
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def eliminar_rating_invalidos(df: pd.DataFrame, min_val: int = 1, max_val: int = 5) -> tuple[pd.DataFrame, dict]:
    filas_antes = len(df)
    df_limpio = df[df["overall"].between(min_val, max_val)].copy()
    filas_eliminadas = filas_antes - len(df_limpio)
    return df_limpio, {"filas_eliminadas": filas_eliminadas}


def limpiar_espacios(df: pd.DataFrame, columnas: list | None = None) -> tuple[pd.DataFrame, dict]:
    cols = columnas if columnas else list(df.select_dtypes(include=["object", "str"]).columns)
    total_modificadas = 0
    for col in cols:
        if col in df.columns:
            antes = df[col].str.strip() != df[col]
            df[col] = df[col].str.strip()
            total_modificadas += antes.sum()
    return df, {"celdas_modificadas": int(total_modificadas)}


def limpiar_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    resultados = {}

    df, r = eliminar_duplicados(df)
    resultados["duplicados"] = r

    df, r = eliminar_nulos(df)
    resultados["nulos"] = r

    df, r = eliminar_reviews_vacias(df)
    resultados["reviews_vacias"] = r

    df, r = eliminar_rating_invalidos(df)
    resultados["rating_invalidos"] = r

    df, r = limpiar_espacios(df)
    resultados["espacios"] = r

    return df, resultados
