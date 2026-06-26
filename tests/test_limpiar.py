import pandas as pd
import pytest

from src.etl.limpiar import (
    _tiene_tipo_no_hashable,
    eliminar_duplicados,
    eliminar_nulos,
    eliminar_rating_invalidos,
    eliminar_reviews_vacias,
    limpiar_dataset,
    limpiar_espacios,
)


class TestTieneTipoNoHashable:
    def test_columna_con_listas(self):
        s = pd.Series([[1, 2], [3, 4]])
        assert _tiene_tipo_no_hashable(s) is True

    def test_columna_string(self):
        s = pd.Series(["a", "b"])
        assert _tiene_tipo_no_hashable(s) is False

    def test_columna_numerica(self):
        s = pd.Series([1, 2, 3])
        assert _tiene_tipo_no_hashable(s) is False

    def test_columna_vacia(self):
        s = pd.Series(dtype="object")
        assert _tiene_tipo_no_hashable(s) is False


class TestEliminarDuplicados:
    def test_sin_duplicados(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        r, reporte = eliminar_duplicados(df)
        assert len(r) == 3
        assert reporte["filas_eliminadas"] == 0

    def test_con_duplicados(self):
        df = pd.DataFrame({"a": [1, 2, 2, 3], "b": ["x", "y", "y", "z"]})
        r, reporte = eliminar_duplicados(df)
        assert len(r) == 3
        assert reporte["filas_eliminadas"] == 1

    def test_con_subset(self):
        df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", "y", "z"]})
        r, reporte = eliminar_duplicados(df, subset=["a"])
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 1

    def test_columna_con_listas_no_crash(self):
        df = pd.DataFrame({"a": [1, 1], "b": [[1, 2], [1, 2]]})
        r, reporte = eliminar_duplicados(df)
        assert reporte["filas_eliminadas"] == 1


class TestEliminarNulos:
    def test_sin_nulos(self):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        r, reporte = eliminar_nulos(df)
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 0

    def test_con_nulos(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})
        r, reporte = eliminar_nulos(df)
        assert len(r) == 1
        assert reporte["filas_eliminadas"] == 2

    def test_con_subset(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
        r, reporte = eliminar_nulos(df, subset=["a"])
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 1

    def test_sin_nulos_en_subset(self):
        df = pd.DataFrame({"a": [1, None], "b": ["x", "y"]})
        r, reporte = eliminar_nulos(df, subset=["b"])
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 0


class TestEliminarReviewsVacias:
    def test_sin_vacias(self):
        df = pd.DataFrame({"reviewText": ["bueno", "malo", "regular"]})
        r, reporte = eliminar_reviews_vacias(df)
        assert len(r) == 3
        assert reporte["filas_eliminadas"] == 0

    def test_con_vacias(self):
        df = pd.DataFrame({"reviewText": ["bueno", "", "   ", "malo"]})
        r, reporte = eliminar_reviews_vacias(df)
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 2

    def test_todas_vacias(self):
        df = pd.DataFrame({"reviewText": ["", "", ""]})
        r, reporte = eliminar_reviews_vacias(df)
        assert len(r) == 0
        assert reporte["filas_eliminadas"] == 3

    def test_con_nulos_en_review_text(self):
        df = pd.DataFrame({"reviewText": ["hola", None, ""]})
        r, reporte = eliminar_reviews_vacias(df)
        assert len(r) == 1
        assert reporte["filas_eliminadas"] == 2


class TestEliminarRatingInvalidos:
    def test_todos_validos(self):
        df = pd.DataFrame({"overall": [1, 3, 5]})
        r, reporte = eliminar_rating_invalidos(df)
        assert len(r) == 3
        assert reporte["filas_eliminadas"] == 0

    def test_con_invalidos(self):
        df = pd.DataFrame({"overall": [0, 1, 5, 6]})
        r, reporte = eliminar_rating_invalidos(df)
        assert len(r) == 2
        assert reporte["filas_eliminadas"] == 2

    def test_todos_invalidos(self):
        df = pd.DataFrame({"overall": [0, 6, -1]})
        r, reporte = eliminar_rating_invalidos(df)
        assert len(r) == 0
        assert reporte["filas_eliminadas"] == 3

    def test_rango_personalizado(self):
        df = pd.DataFrame({"overall": [3, 4, 5, 6]})
        r, reporte = eliminar_rating_invalidos(df, min_val=3, max_val=5)
        assert len(r) == 3
        assert reporte["filas_eliminadas"] == 1


class TestLimpiarEspacios:
    def test_sin_espacios(self):
        df = pd.DataFrame({"a": ["hola", "mundo"], "b": ["x", "y"]})
        r, reporte = limpiar_espacios(df)
        assert reporte["celdas_modificadas"] == 0
        assert list(r["a"]) == ["hola", "mundo"]

    def test_con_espacios(self):
        df = pd.DataFrame({"a": ["  hola ", "mundo  "], "b": ["x", "y"]})
        r, reporte = limpiar_espacios(df)
        assert reporte["celdas_modificadas"] == 2
        assert list(r["a"]) == ["hola", "mundo"]

    def test_columnas_especificas(self):
        df = pd.DataFrame({"a": ["  hola ", "mundo  "], "b": ["  x  ", "  y  "]})
        r, reporte = limpiar_espacios(df, columnas=["a"])
        assert reporte["celdas_modificadas"] == 2
        assert list(r["b"]) == ["  x  ", "  y  "]

    def test_sin_columnas_string(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        r, reporte = limpiar_espacios(df)
        assert reporte["celdas_modificadas"] == 0

    def test_no_afecta_columnas_con_listas(self):
        df = pd.DataFrame({"texto": [" hola "], "lista": [[1, 2, 3]]})
        r, reporte = limpiar_espacios(df)
        assert r["lista"].iloc[0] == [1, 2, 3]
        assert reporte["celdas_modificadas"] == 1


class TestLimpiarDataset:
    def test_integracion_con_dataset_real(self):
        from src.etl.cargador import cargar_dataset
        from pathlib import Path

        ruta = Path(__file__).resolve().parents[1] / "data" / "raw" / "Electronics_5.json"
        df = cargar_dataset(str(ruta))
        df_limpio, reporte = limpiar_dataset(df)

        assert isinstance(df_limpio, pd.DataFrame)
        assert len(df_limpio) < len(df)
        assert df_limpio.isna().sum().sum() == 0
        assert (df_limpio["reviewText"].str.strip() == "").sum() == 0
        assert df_limpio["overall"].between(1, 5).all()

        claves = {"duplicados", "nulos", "reviews_vacias", "rating_invalidos", "espacios"}
        assert claves.issubset(reporte.keys())

    def test_reporte_contiene_filas_eliminadas(self):
        from src.etl.cargador import cargar_dataset
        from pathlib import Path

        ruta = Path(__file__).resolve().parents[1] / "data" / "raw" / "Electronics_5.json"
        df = cargar_dataset(str(ruta))
        _, reporte = limpiar_dataset(df)

        for key in ["duplicados", "nulos", "reviews_vacias", "rating_invalidos"]:
            assert "filas_eliminadas" in reporte[key]
        assert "celdas_modificadas" in reporte["espacios"]

    def test_dataframe_vacio(self):
        df = pd.DataFrame()
        r, reporte = limpiar_dataset(df)
        assert len(r) == 0
