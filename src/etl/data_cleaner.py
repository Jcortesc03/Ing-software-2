# ============================================================
# CELDA 4.1 — Clase DataCleaner completa para el proyecto
# Integra limpieza + optimización + medición de latencia
# ============================================================

class DataCleaner:
    """
    Módulo de limpieza y optimización de datos para el proyecto semestral.

    Responsabilidad única: tomar un DataFrame crudo y devolver un DataFrame
    limpio, optimizado en memoria, con todos los eventos documentados en logs.

    Uso típico:
        cleaner = DataCleaner(nombre_proyecto='ventas_2024')
        df_limpio, reporte = cleaner.limpiar(df_crudo)
    """

    def __init__(self, nombre_proyecto: str = 'proyecto'):
        """
        Inicializa el DataCleaner.

        Args:
            nombre_proyecto (str): Nombre del proyecto para identificar los logs.
        """
        self.nombre_proyecto = nombre_proyecto
        self.logger          = logging.getLogger(f'{nombre_proyecto}.DataCleaner')
        self.timer           = PipelineTimer(f'{nombre_proyecto}.limpieza')
        self.reporte_calidad = {}   # Se llena durante el proceso
        self.logger.info('DataCleaner inicializado')


    def diagnosticar_calidad(self, df: pd.DataFrame) -> dict:
        """
        Analiza la calidad del DataFrame: nulos, duplicados y tipos de datos.

        Args:
            df (pd.DataFrame): DataFrame a diagnosticar.

        Returns:
            dict con métricas de calidad detalladas.
        """
        self.logger.info('Iniciando diagnóstico de calidad de datos')

        # Calcular métricas de nulos
        nulos_col   = df.isna().sum()
        pct_nulos   = (nulos_col / len(df) * 100).round(2)
        n_dup       = df.duplicated().sum()
        total_nulos = nulos_col.sum()

        reporte = {
            'filas_totales':    len(df),
            'columnas':         df.shape[1],
            'duplicados':       int(n_dup),
            'pct_duplicados':   round(n_dup / len(df) * 100, 2),
            'nulos_totales':    int(total_nulos),
            'pct_nulos_global': round(total_nulos / (len(df) * df.shape[1]) * 100, 2),
            'nulos_por_col':    nulos_col.to_dict(),
            'pct_nulos_col':    pct_nulos.to_dict(),
            'tipos_datos':      df.dtypes.astype(str).to_dict(),
            'memoria_mb':       round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        }

        # Registrar hallazgos según severidad
        self.logger.info(f'Dimensiones: {len(df):,} filas × {df.shape[1]} columnas')
        self.logger.info(f'Duplicados:  {n_dup:,} ({reporte["pct_duplicados"]}%)')

        if total_nulos == 0:
            self.logger.info('Calidad de nulos: PERFECTA — sin valores faltantes')
        else:
            self.logger.warning(f'Nulos totales: {total_nulos:,} ({reporte["pct_nulos_global"]}% del total)')
            for col, n in nulos_col[nulos_col > 0].items():
                pct = pct_nulos[col]
                nivel = 'ERROR' if pct > 30 else ('WARNING' if pct > 10 else 'INFO')
                getattr(self.logger, nivel.lower())(f'  {col}: {n:,} nulos ({pct}%)')

        self.reporte_calidad = reporte
        return reporte


    def limpiar(self, df: pd.DataFrame,
                estrategia_nulos: str = 'mediana',
                optimizar_ram: bool   = True) -> tuple:
        """
        Limpia el DataFrame aplicando: eliminación de duplicados,
        imputación de nulos y (opcionalmente) optimización de tipos.

        Args:
            df (pd.DataFrame):         DataFrame crudo a limpiar.
            estrategia_nulos (str):    'mediana', 'media' o 'eliminar'.
            optimizar_ram (bool):      Si True, aplica casteo de tipos.

        Returns:
            tuple: (df_limpio, reporte_dict)
        """
        self.logger.info(f'=== INICIO DE LIMPIEZA — {self.nombre_proyecto} ===')
        self.timer.iniciar()

        df_out = df.copy()
        filas_inicio = len(df_out)

        # ── Diagnóstico inicial ──────────────────────────
        reporte_inicio = self.diagnosticar_calidad(df_out)
        self.timer.marcar('diagnostico')

        # ── Paso 1: Eliminar duplicados ──────────────────
        n_dup = df_out.duplicated().sum()
        df_out = df_out.drop_duplicates()
        self.logger.info(f'Duplicados eliminados: {n_dup:,} filas')
        self.timer.marcar('eliminar_duplicados')

        # ── Paso 2: Imputar nulos ────────────────────────
        for col in df_out.columns:
            n_nulos = df_out[col].isna().sum()
            if n_nulos == 0:
                continue

            tipo = df_out[col].dtype

            if tipo in ['object', 'category']:
                # Categórico: imputar con valor por defecto
                df_out[col] = df_out[col].fillna('Sin Datos')
                self.logger.info(f'  {col}: {n_nulos} nulos → "Sin Datos"')

            elif estrategia_nulos == 'eliminar':
                df_out = df_out.dropna(subset=[col])
                self.logger.info(f'  {col}: {n_nulos} filas eliminadas por nulos')

            elif estrategia_nulos == 'media':
                valor = df_out[col].mean()
                df_out[col] = df_out[col].fillna(valor)
                self.logger.info(f'  {col}: {n_nulos} nulos → media {valor:.2f}')

            else:  # mediana (defecto — más robusta)
                valor = df_out[col].median()
                df_out[col] = df_out[col].fillna(valor)
                self.logger.info(f'  {col}: {n_nulos} nulos → mediana {valor:.2f}')

        self.timer.marcar('imputacion_nulos')

        # ── Paso 3: Optimizar memoria ─────────────────────
        mem_antes = df_out.memory_usage(deep=True).sum() / 1024**2
        if optimizar_ram:
            df_out = optimizar_memoria_df(df_out, verbose=False)
        mem_despues = df_out.memory_usage(deep=True).sum() / 1024**2
        self.logger.info(f'RAM: {mem_antes:.1f} MB → {mem_despues:.1f} MB ({(1-mem_despues/mem_antes)*100:.0f}% reducción)')
        self.timer.marcar('optimizacion_ram')

        # ── Reporte final ─────────────────────────────────
        metricas_timer = self.timer.reporte()

        reporte_final = {
            'filas_entrada':    filas_inicio,
            'filas_salida':     len(df_out),
            'filas_eliminadas': filas_inicio - len(df_out),
            'nulos_resueltos':  reporte_inicio['nulos_totales'],
            'ram_antes_mb':     round(mem_antes, 2),
            'ram_despues_mb':   round(mem_despues, 2),
            'pct_reduccion_ram':round((1 - mem_despues/mem_antes) * 100, 1) if mem_antes > 0 else 0,
            'latencia_seg':     metricas_timer.get('total_segundos', 0),
            'cuello_botella':   metricas_timer.get('cuello', 'N/A'),
        }

        self.logger.info(f'=== FIN DE LIMPIEZA: {len(df_out):,} filas limpias ===')
        return df_out, reporte_final


print('✅ Clase DataCleaner definida.')
print('   Métodos: diagnosticar_calidad(), limpiar()')

# ============================================================
# CELDA 4.2 — Probar DataCleaner con el dataset corporativo
# ============================================================

print('🧪 Prueba completa del DataCleaner:')
print('='*55)

# Instanciar y ejecutar sobre el dataset sucio del Bloque 1
cleaner = DataCleaner(nombre_proyecto='empleados_corporativo')

# Limpiar con estrategia mediana y optimización de RAM activada
df_resultado, reporte = cleaner.limpiar(
    df            = df_sucio,
    estrategia_nulos = 'mediana',
    optimizar_ram    = True
)

# Mostrar el reporte consolidado
print('\n📄 REPORTE CONSOLIDADO DE LIMPIEZA:')
print('='*55)
for clave, valor in reporte.items():
    print(f'  {clave:<25}: {valor}')

# Verificaciones de integridad
assert df_resultado.isna().sum().sum() == 0, '❌ Aún hay valores nulos'
assert df_resultado.duplicated().sum()  == 0, '❌ Aún hay duplicados'
print('\n✅ DataCleaner funciona correctamente sobre el dataset de prueba')