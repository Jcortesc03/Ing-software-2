from pathlib import Path

import pandas as pd
import pytest

from src.etl.cargador import cargar_json

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DATASET_PATH = DATA_DIR / "Electronics_5.json"


@pytest.fixture(scope="session")
def df() -> pd.DataFrame:
    return cargar_json(str(DATASET_PATH))


def test_cargar_json_retorna_dataframe(df):
    assert isinstance(df, pd.DataFrame)


def test_cargar_json_no_vacio(df):
    assert len(df) > 0


def test_cargar_json_columnas_esperadas(df):
    expected = {"reviewerID", "asin", "overall", "reviewText", "summary", "unixReviewTime", "reviewTime"}
    assert expected.issubset(set(df.columns)), f"Faltan columnas. Obtenidas: {list(df.columns)}"


def test_cargar_json_tipos(df):
    assert pd.api.types.is_numeric_dtype(df["overall"])
    assert pd.api.types.is_string_dtype(df["asin"])


@pytest.mark.parametrize("col", ["reviewerID", "asin"])
def test_cargar_json_sin_nulos_en_columnas_clave(df, col):
    assert df[col].isna().sum() == 0, f"Columna '{col}' tiene valores nulos"


def test_cargar_json_shape_consistente(df):
    assert df.shape[1] >= 7
