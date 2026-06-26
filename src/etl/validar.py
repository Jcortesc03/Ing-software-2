from pathlib import Path

import pandas as pd

from src.etl.cargador import cargar_dataset


def validar_existencia(ruta: str) -> dict:
    existe = Path(ruta).exists()
    return {"valido": existe, "mensaje": "El archivo existe" if existe else f"No se encuentra: {ruta}"}


def validar_columnas(df: pd.DataFrame, columnas_esperadas: list) -> dict:
    reales = set(df.columns)
    esperadas = set(columnas_esperadas)
    faltantes = esperadas - reales
    sobrantes = reales - esperadas
    valido = len(faltantes) == 0
    return {
        "valido": valido,
        "columnas_faltantes": sorted(faltantes),
        "columnas_sobrantes": sorted(sobrantes),
    }


def validar_nulos(df: pd.DataFrame, columnas: list | None = None) -> dict:
    cols = columnas if columnas else list(df.columns)
    nulos = {col: int(df[col].isna().sum()) for col in cols}
    total = sum(nulos.values())
    return {
        "valido": total == 0,
        "nulos_totales": total,
        "nulos_por_columna": nulos,
    }


def validar_tipos(df: pd.DataFrame, esquema: dict) -> dict:
    resultados = {}
    for col, tipo_esperado in esquema.items():
        if col in df.columns:
            tipo_real = str(df[col].dtype)
            resultados[col] = {"esperado": tipo_esperado, "real": tipo_real, "valido": tipo_real == tipo_esperado}
        else:
            resultados[col] = {"esperado": tipo_esperado, "real": None, "valido": False}
    valido = all(r["valido"] for r in resultados.values())
    return {"valido": valido, "detalles": resultados}


def validar_vacios(df: pd.DataFrame) -> dict:
    valido = len(df) > 0
    return {"valido": valido, "filas": len(df)}


def validar_dataset(ruta: str, columnas_esperadas: list, esquema: dict | None = None) -> dict:
    resultado = {"existencia": validar_existencia(ruta)}

    if not resultado["existencia"]["valido"]:
        return {"valido": False, "errores": [resultado["existencia"]["mensaje"]], **resultado}

    df = cargar_dataset(ruta)

    resultado["vacios"] = validar_vacios(df)
    resultado["columnas"] = validar_columnas(df, columnas_esperadas)
    resultado["nulos"] = validar_nulos(df)
    if esquema:
        resultado["tipos"] = validar_tipos(df, esquema)

    errores = []
    if not resultado["vacios"]["valido"]:
        errores.append("El dataset está vacío")
    if not resultado["columnas"]["valido"]:
        errores.append(f"Faltan columnas: {resultado['columnas']['columnas_faltantes']}")
    if not resultado["nulos"]["valido"]:
        errores.append(f"Hay {resultado['nulos']['nulos_totales']} valores nulos")
    if esquema and not resultado["tipos"]["valido"]:
        errores.append("Los tipos de datos no coinciden con el esquema esperado")

    return {"valido": len(errores) == 0, "errores": errores, **resultado}
