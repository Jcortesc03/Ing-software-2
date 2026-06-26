from pathlib import Path

import pandas as pd
import pytest

from src.etl.validar import (
    validar_columnas,
    validar_dataset,
    validar_existencia,
    validar_nulos,
    validar_tipos,
    validar_vacios,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DATASET_PATH = DATA_DIR / "Electronics_5.json"

COLUMNAS = [
    "reviewerID", "asin", "reviewerName", "helpful",
    "reviewText", "overall", "summary", "unixReviewTime", "reviewTime",
]

ESQUEMA = {
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


class TestValidarExistencia:
    def test_archivo_existe(self):
        res = validar_existencia(str(DATASET_PATH))
        assert res["valido"] is True
        assert res["mensaje"] == "El archivo existe"

    def test_archivo_no_existe(self):
        res = validar_existencia("no_existe.json")
        assert res["valido"] is False
        assert "No se encuentra" in res["mensaje"]


class TestValidarColumnas:
    def test_columnas_coinciden(self):
        df = pd.DataFrame(columns=COLUMNAS)
        res = validar_columnas(df, COLUMNAS)
        assert res["valido"] is True
        assert res["columnas_faltantes"] == []

    def test_faltan_columnas(self):
        df = pd.DataFrame(columns=["a", "b"])
        res = validar_columnas(df, ["a", "b", "c"])
        assert res["valido"] is False
        assert "c" in res["columnas_faltantes"]

    def test_sobran_columnas(self):
        df = pd.DataFrame(columns=["a", "b", "c_extra"])
        res = validar_columnas(df, ["a", "b"])
        assert res["valido"] is True
        assert "c_extra" in res["columnas_sobrantes"]


class TestValidarNulos:
    def test_sin_nulos(self):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        res = validar_nulos(df)
        assert res["valido"] is True
        assert res["nulos_totales"] == 0

    def test_con_nulos(self):
        df = pd.DataFrame({"a": [1, None], "b": ["x", None]})
        res = validar_nulos(df)
        assert res["valido"] is False
        assert res["nulos_totales"] == 2

    def test_nulos_en_columnas_especificas(self):
        df = pd.DataFrame({"a": [1, None], "b": ["x", "y"], "c": [None, None]})
        res = validar_nulos(df, columnas=["a"])
        assert res["nulos_totales"] == 1
        assert "a" in res["nulos_por_columna"]
        assert "b" not in res["nulos_por_columna"]


class TestValidarTipos:
    def test_tipos_coinciden(self):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        esquema = {"a": "int64", "b": "str"}
        res = validar_tipos(df, esquema)
        assert res["valido"] is True

    def test_tipo_incorrecto(self):
        df = pd.DataFrame({"a": [1.5, 2.5], "b": ["x", "y"]})
        esquema = {"a": "int64", "b": "str"}
        res = validar_tipos(df, esquema)
        assert res["valido"] is False
        assert res["detalles"]["a"]["valido"] is False

    def test_columna_faltante_en_esquema(self):
        df = pd.DataFrame({"a": [1, 2]})
        esquema = {"a": "int64", "b": "str"}
        res = validar_tipos(df, esquema)
        assert res["valido"] is False
        assert res["detalles"]["b"]["real"] is None


class TestValidarVacios:
    def test_no_vacio(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        res = validar_vacios(df)
        assert res["valido"] is True
        assert res["filas"] == 3

    def test_vacio(self):
        df = pd.DataFrame()
        res = validar_vacios(df)
        assert res["valido"] is False
        assert res["filas"] == 0

    def test_vacio_con_columnas(self):
        df = pd.DataFrame({"a": pd.Series(dtype="int64")})
        res = validar_vacios(df)
        assert res["valido"] is False


class TestValidarDataset:
    def test_integracion_completa(self):
        res = validar_dataset(str(DATASET_PATH), COLUMNAS, ESQUEMA)
        assert res["existencia"]["valido"] is True
        assert res["vacios"]["valido"] is True
        assert res["columnas"]["valido"] is True
        assert res["tipos"]["valido"] is True

    def test_integracion_sin_esquema(self):
        res = validar_dataset(str(DATASET_PATH), COLUMNAS)
        assert "tipos" not in res
        assert isinstance(res["valido"], bool)

    def test_ruta_inexistente(self):
        res = validar_dataset("fake.json", COLUMNAS)
        assert res["valido"] is False
        assert any("No se encuentra" in e for e in res["errores"])
