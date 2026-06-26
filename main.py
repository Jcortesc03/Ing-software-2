"""
Pipeline ETL completo: Carga -> Validacion -> Limpieza -> Transformacion
"""

import subprocess
import sys
from pathlib import Path

from src.etl.cargador import cargar_dataset
from src.etl.limpiar import limpiar_dataset
from src.etl.transformador import transformar_dataset
from src.etl.validar import validar_dataset
from src.utils.logger import Logger
from src.utils.performance import PerformanceMonitor

RUTA_DATASET = "data/raw/Electronics_5.json"

COLUMNAS = [
    "reviewerID", "asin", "reviewerName", "helpful",
    "reviewText", "overall", "summary", "unixReviewTime", "reviewTime",
]

ESQUEMA_TIPOS = {
    "reviewerID": "str",
    "asin": "str",
    "reviewerName": "str",
    "helpful": "object",
    "reviewText": "str",
    "overall": "int64",
    "summary": "str",
    "unixReviewTime": "int64",
    "reviewTime": "str",
}


def imprimir_encabezado(log: Logger):
    log.divider()
    log.info("PIPELINE ETL - Amazon Electronics Reviews")
    log.info(f"Dataset: {RUTA_DATASET}")
    log.divider()


def imprimir_resumen(df_original, df_limpio, df_transformado, ruta_final, log: Logger):
    log.divider()
    log.info("RESUMEN FINAL DEL PIPELINE")
    log.divider()
    log.info(f"  Carga:       {df_original.shape[0]:>12,} filas x {df_original.shape[1]} cols")
    log.info(f"  Limpieza:    {df_limpio.shape[0]:>12,} filas x {df_limpio.shape[1]} cols  "
             f"({df_original.shape[0] - df_limpio.shape[0]:,} eliminadas)")
    cols_nuevas = df_transformado.shape[1] - df_limpio.shape[1]
    log.info(f"  Transform:   {df_transformado.shape[0]:>12,} filas x {df_transformado.shape[1]} cols  "
             f"({cols_nuevas} nuevas columnas)")
    log.info(f"  Salida:      {ruta_final}")
    log.divider()


def main():
    log = Logger("Main")
    perf = PerformanceMonitor()

    imprimir_encabezado(log)
    perf.iniciar()

    # ── 1. CARGA ──────────────────────────────────────────────
    log.paso("ETL", "Fase 1/4: Carga de datos")
    try:
        df = cargar_dataset(RUTA_DATASET, logger=log)
        perf.marcar("1_carga")
    except FileNotFoundError:
        log.warning("ETL", f"Archivo no encontrado: {RUTA_DATASET}")
        log.paso("ETL", "Ejecutando src/etl/dataset.py para descargar dataset...")
        result = subprocess.run(
            [sys.executable, "src/etl/dataset.py"],
            capture_output=True, text=True,
        )
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                log.info("dataset.py", line.strip())
        if result.returncode != 0:
            log.error("ETL", f"dataset.py fallo:\n{result.stderr}")
            sys.exit(1)
        log.ok("ETL", "Dataset descargado, reintentando carga...")
        df = cargar_dataset(RUTA_DATASET, logger=log)
        perf.marcar("1_carga")
    except Exception as e:
        log.error("ETL", f"Error en carga: {e}")
        sys.exit(1)

    # ── 2. VALIDACION ─────────────────────────────────────────
    log.paso("ETL", "Fase 2/4: Validacion de datos")
    resultado_val = validar_dataset(RUTA_DATASET, COLUMNAS, ESQUEMA_TIPOS, logger=log)
    perf.marcar("2_validacion")

    if not resultado_val["valido"]:
        log.warning("ETL", f"Validacion reporto {len(resultado_val['errores'])} problema(s)")
        for e in resultado_val["errores"]:
            log.warning("ETL", f"  - {e}")
    else:
        log.ok("ETL", "Dataset validado correctamente")

    # ── 3. LIMPIEZA ───────────────────────────────────────────
    log.paso("ETL", "Fase 3/4: Limpieza de datos")
    df_limpio, reporte_limpieza = limpiar_dataset(df, logger=log)
    perf.marcar("3_limpieza")

    total_eliminadas = sum(
        v["filas_eliminadas"] for k, v in reporte_limpieza.items() if "filas_eliminadas" in v
    )
    log.ok("ETL", f"Limpieza finalizada: {total_eliminadas:,} filas eliminadas")

    # ── 4. TRANSFORMACION ─────────────────────────────────────
    log.paso("ETL", "Fase 4/4: Transformacion de datos")
    df_transformado, ruta_final, reporte_transform = transformar_dataset(
        df_limpio, nombre_salida="electronics_processed",
        logger=log,
    )
    perf.marcar("4_transformacion")

    # ── RESUMEN ───────────────────────────────────────────────
    imprimir_resumen(df, df_limpio, df_transformado, ruta_final, log)
    perf.imprimir_reporte()

    log.ok("ETL", "Pipeline ETL completado exitosamente")


if __name__ == "__main__":
    main()
