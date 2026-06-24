# ============================================================
# CELDA 4.3 — LABORATORIO: Aplica DataCleaner a TU dataset
# ============================================================
#
# INSTRUCCIONES PARA EL EQUIPO:
# ─────────────────────────────
# Opción A: Dataset ya cargado en memoria (Sesión 6)
#   Cambia RUTA_DATASET por la variable de tu DataLoader
#
# Opción B: Cargar desde Google Drive
#   from google.colab import drive
#   drive.mount('/content/drive')
#   RUTA_DATASET = '/content/drive/MyDrive/proyecto/dataset.parquet'
#
# Opción C: Cargar desde AWS S3 (requiere credenciales)
#   import boto3, s3fs
#   RUTA_DATASET = 's3://mi-bucket/datos/dataset.parquet'
#   df_mi_proyecto = pd.read_parquet(RUTA_DATASET, storage_options={...})
# ─────────────────────────────────────────────────────────────

# 🔴 REEMPLAZA CON TU DATASET REAL
# Si no tienes el dataset disponible aún, usa df_banco de esta sesión
df_mi_proyecto = df_banco.copy()   # ← REEMPLAZA con tu DataFrame real
NOMBRE_MI_PROYECTO = 'mi_proyecto_bigdata'   # ← Pon el nombre de tu proyecto

print(f'📊 Dataset del proyecto: {len(df_mi_proyecto):,} filas × {df_mi_proyecto.shape[1]} columnas')
print(f'   Nombre: {NOMBRE_MI_PROYECTO}')
print()

# ── DEMOSTRACIÓN 1: Reporte de calidad de datos ────────────
print('🔍 DEMOSTRACIÓN 1 — Reporte de calidad:')
cleaner_proyecto = DataCleaner(nombre_proyecto=NOMBRE_MI_PROYECTO)
rep_calidad = cleaner_proyecto.diagnosticar_calidad(df_mi_proyecto)

print(f'  Filas:      {rep_calidad["filas_totales"]:,}')
print(f'  Nulos:      {rep_calidad["nulos_totales"]:,} ({rep_calidad["pct_nulos_global"]}%)')
print(f'  Duplicados: {rep_calidad["duplicados"]:,} ({rep_calidad["pct_duplicados"]}%)')
print(f'  RAM actual: {rep_calidad["memoria_mb"]} MB')

# ── DEMOSTRACIÓN 2 + 3: Limpiar con reporte completo ───────
print('\n⚡ DEMOSTRACIÓN 2+3 — Limpieza, optimización y latencia:')
df_mi_limpio, reporte_completo = cleaner_proyecto.limpiar(
    df               = df_mi_proyecto,
    estrategia_nulos = 'mediana',
    optimizar_ram    = True
)

print(f'\n📄 REPORTE FINAL DEL EQUIPO:')
print('='*55)
print(f'  Filas entrada:        {reporte_completo["filas_entrada"]:,}')
print(f'  Filas salida:         {reporte_completo["filas_salida"]:,}')
print(f'  Filas eliminadas:     {reporte_completo["filas_eliminadas"]:,}')
print(f'  Nulos resueltos:      {reporte_completo["nulos_resueltos"]:,}')
print(f'  RAM antes:            {reporte_completo["ram_antes_mb"]} MB')
print(f'  RAM después:          {reporte_completo["ram_despues_mb"]} MB')
print(f'  Reducción RAM:        {reporte_completo["pct_reduccion_ram"]}%')
print(f'  Latencia total:       {reporte_completo["latencia_seg"]:.3f}s')
print(f'  Cuello de botella:    {reporte_completo["cuello_botella"]}')
print('='*55)
print('\n✅ Las 3 demostraciones del laboratorio completadas')