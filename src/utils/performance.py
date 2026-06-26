import time

import pandas as pd


class PerformanceMonitor:
    def __init__(self):
        self._inicio: float | None = None
        self._marcas: list[tuple[str, float]] = []

    def iniciar(self):
        self._inicio = time.perf_counter()
        self._marcas = []

    def marcar(self, nombre: str):
        ahora = time.perf_counter()
        self._marcas.append((nombre, ahora))

    def reporte(self) -> dict:
        if not self._marcas:
            return {}
        _, t0 = self._marcas[0]
        pasos = []
        for i, (nombre, t) in enumerate(self._marcas):
            duracion = t - (self._marcas[i - 1][1] if i > 0 else t0)
            pasos.append({"paso": nombre, "duracion_seg": round(duracion, 4)})
        total_seg = round(self._marcas[-1][1] - t0, 4)
        cuello = max(pasos, key=lambda p: p["duracion_seg"])["paso"] if pasos else None
        return {
            "pasos": pasos,
            "total_segundos": total_seg,
            "cuello": cuello,
        }

    def imprimir_reporte(self):
        reporte = self.reporte()
        if not reporte:
            return
        self._imprimir(f"{'Paso':<35} {'Duracion (s)':<15}")
        self._imprimir("-" * 50)
        for p in reporte["pasos"]:
            indicador = " << CUELLO" if p["paso"] == reporte["cuello"] else ""
            self._imprimir(f"{p['paso']:<35} {p['duracion_seg']:<15.4f}{indicador}")
        self._imprimir("-" * 50)
        self._imprimir(f"{'TOTAL':<35} {reporte['total_segundos']:<15.4f}")

    def _imprimir(self, mensaje: str):
        import sys
        try:
            sys.stdout.write(mensaje + "\n")
        except UnicodeEncodeError:
            linea = mensaje.encode("ascii", errors="replace").decode("ascii")
            sys.stdout.write(linea + "\n")
        sys.stdout.flush()


def memoria_df(df: pd.DataFrame) -> float:
    return round(df.memory_usage(deep=True).sum() / 1024**2, 2)
