from pathlib import Path

import pandas as pd

from src.etl.cargador import cargar_dataset
from src.utils.logger import Logger
from src.utils.performance import PerformanceMonitor


def validar_existencia(ruta: str, logger: Logger | None = None) -> dict:
    log = logger or Logger("Validador")
    log.paso("Existencia", f"Verificando: {ruta}")
    existe = Path(ruta).exists()
    if existe:
        log.ok("Existencia", "Archivo encontrado")
    else:
        log.error("Existencia", f"No se encuentra: {ruta}")
    return {"valido": existe, "mensaje": "El archivo existe" if existe else f"No se encuentra: {ruta}"}


def validar_columnas(df: pd.DataFrame, columnas_esperadas: list, logger: Logger | None = None) -> dict:
    log = logger or Logger("Validador")
    log.paso("Columnas", "Verificando columnas esperadas")
    reales = set(df.columns)
    esperadas = set(columnas_esperadas)
    faltantes = esperadas - reales
    sobrantes = reales - esperadas
    valido = len(faltantes) == 0
    if valido:
        log.ok("Columnas", f"Todas las {len(columnas_esperadas)} columnas presentes")
    else:
        log.error("Columnas", f"Faltan: {sorted(faltantes)}")
    return {
        "valido": valido,
        "columnas_faltantes": sorted(faltantes),
        "columnas_sobrantes": sorted(sobrantes),
    }


def validar_nulos(df: pd.DataFrame, columnas: list | None = None, logger: Logger | None = None) -> dict:
    log = logger or Logger("Validador")
    log.paso("Nulos", "Analizando valores nulos")
    cols = columnas if columnas else list(df.columns)
    nulos = {col: int(df[col].isna().sum()) for col in cols}
    total = sum(nulos.values())
    if total == 0:
        log.ok("Nulos", "Sin valores nulos")
    else:
        log.warning("Nulos", f"{total} valores nulos encontrados")
        for col, n in nulos.items():
            if n > 0:
                log.info(f"  {col}: {n} nulos")
    return {
        "valido": total == 0,
        "nulos_totales": total,
        "nulos_por_columna": nulos,
    }


def validar_tipos(df: pd.DataFrame, esquema: dict, logger: Logger | None = None) -> dict:
    log = logger or Logger("Validador")
    log.paso("Tipos", "Verificando tipos de datos")
    resultados = {}
    for col, tipo_esperado in esquema.items():
        if col in df.columns:
            tipo_real = str(df[col].dtype)
            ok = tipo_real == tipo_esperado
            resultados[col] = {"esperado": tipo_esperado, "real": tipo_real, "valido": ok}
            if not ok:
                log.error("Tipos", f"{col}: esperado {tipo_esperado}, real {tipo_real}")
        else:
            resultados[col] = {"esperado": tipo_esperado, "real": None, "valido": False}
            log.error("Tipos", f"{col}: columna no encontrada")
    valido = all(r["valido"] for r in resultados.values())
    if valido:
        log.ok("Tipos", "Todos los tipos coinciden")
    return {"valido": valido, "detalles": resultados}


def validar_vacios(df: pd.DataFrame, logger: Logger | None = None) -> dict:
    log = logger or Logger("Validador")
    log.paso("Vacios", "Verificando si el dataset esta vacio")
    valido = len(df) > 0
    if valido:
        log.ok("Vacios", f"{len(df):,} filas encontradas")
    else:
        log.error("Vacios", "El dataset esta vacio")
    return {"valido": valido, "filas": len(df)}


def validar_dataset(ruta: str, columnas_esperadas: list, esquema: dict | None = None,
                    logger: Logger | None = None, perf: PerformanceMonitor | None = None) -> dict:
    log = logger or Logger("Validador")
    timer = perf or PerformanceMonitor()
    timer.iniciar()

    log.divider()
    log.paso("Dataset", "Iniciando validacion completa")
    resultado = {"existencia": validar_existencia(ruta, logger=log)}
    timer.marcar("existencia")

    if not resultado["existencia"]["valido"]:
        log.error("Dataset", "Validacion detenida por archivo inexistente")
        return {"valido": False, "errores": [resultado["existencia"]["mensaje"]], **resultado}

    df = cargar_dataset(ruta, logger=log)
    timer.marcar("carga")

    resultado["vacios"] = validar_vacios(df, logger=log)
    timer.marcar("vacios")
    resultado["columnas"] = validar_columnas(df, columnas_esperadas, logger=log)
    timer.marcar("columnas")
    resultado["nulos"] = validar_nulos(df, logger=log)
    timer.marcar("nulos")
    if esquema:
        resultado["tipos"] = validar_tipos(df, esquema, logger=log)
        timer.marcar("tipos")

    errores = []
    if not resultado["vacios"]["valido"]:
        errores.append("El dataset está vacío")
    if not resultado["columnas"]["valido"]:
        errores.append(f"Faltan columnas: {resultado['columnas']['columnas_faltantes']}")
    if not resultado["nulos"]["valido"]:
        errores.append(f"Hay {resultado['nulos']['nulos_totales']} valores nulos")
    if esquema and not resultado["tipos"]["valido"]:
        errores.append("Los tipos de datos no coinciden con el esquema esperado")

    resumen = {"valido": len(errores) == 0, "errores": errores, **resultado}

    if resumen["valido"]:
        log.ok("Dataset", "Validacion completada sin errores")
    else:
        log.error("Dataset", f"Validacion completada con {len(errores)} error(es)")

    if not perf:
        log.divider()
        timer.imprimir_reporte()
        log.divider()

    return resumen
