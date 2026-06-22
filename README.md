# Proyecto big data

## Desarrollado por:
    -Juan Camilo Cortes
    -Juan Camilo Ibarra
    -Isaac Daniel Moreno
    -Andruw Sarrias

## Estructura del proyecto:
   C:

    ├───docs
    └───src
        ├───analisis
        ├───etl
        ├───modelos
        ├───utils
        └───viz


## Esquema preliminar de bloques ETL



┌───────────────────────────────┐

│ MÓDULO 1: FUENTE DE DATOS     │

│ Responsabilidad: Almacenar    │

│ la base de datos de  reseñas  │ 

│ Capa: Datos                   │

└───────────────┬───────────────┘

                │

                ▼


┌───────────────────────────────┐

│ MÓDULO 2: CARGA DE DATOS      │

│ Responsabilidad: Leer el CSV  │

│ y cargarlo en Pandas          │

│ Capa: Ingesta de Datos        │

└───────────────┬───────────────┘

                │

             ▼

┌───────────────────────────────┐

│ MÓDULO 3: LIMPIEZA DE DATOS   │

│ Responsabilidad: Eliminar     │

│ nulos, duplicados y errores   │

│ Capa: Procesamiento           │

└───────────────┬───────────────┘

                │

                ▼

┌───────────────────────────────┐

│ MÓDULO 4: TRANSFORMACIÓN      │

│ Responsabilidad: Preparar     │

│ variables para el análisis    │

│ Capa: Procesamiento           │

└───────────────┬───────────────┘

                │

                ▼
┌───────────────────────────────┐

│ MÓDULO 5: ANÁLISIS DE DATOS   │

│ Responsabilidad: Obtener      │

│ estadísticas y patrones       │

│ Capa: Negocio                 │

└───────────────┬───────────────┘

                │

                ▼
┌───────────────────────────────┐

│ MÓDULO 6: VISUALIZACIÓN       │

│ Responsabilidad: Generar      │

│ gráficos e informes           │

│ Capa: Presentación            │

└───────────────┬───────────────┘

                │

                 ▼
┌───────────────────────────────┐

│ MÓDULO 7: RESULTADOS          │

│ Responsabilidad: Mostrar      │

│ conclusiones y hallazgos      │

│ Capa: Presentación            │

└───────────────────────────────┘