import sys
from datetime import datetime


class Logger:
    def __init__(self, nombre: str = "ETL", archivo: str | None = None):
        self.nombre = nombre
        self.archivo = archivo

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _escribir(self, mensaje: str):
        try:
            sys.stdout.write(mensaje + "\n")
            sys.stdout.flush()
        except UnicodeEncodeError:
            linea = mensaje.encode("ascii", errors="replace").decode("ascii")
            sys.stdout.write(linea + "\n")
            sys.stdout.flush()
        if self.archivo:
            with open(self.archivo, "a", encoding="utf-8") as f:
                f.write(mensaje + "\n")

    def paso(self, etiqueta: str, mensaje: str = ""):
        texto = f"[{self._timestamp()}] [{self.nombre}]  > {etiqueta} {mensaje}".rstrip()
        self._escribir(texto)

    def ok(self, etiqueta: str, mensaje: str = ""):
        texto = f"[{self._timestamp()}] [{self.nombre}] OK {etiqueta} {mensaje}".rstrip()
        self._escribir(texto)

    def error(self, etiqueta: str, mensaje: str = ""):
        texto = f"[{self._timestamp()}] [{self.nombre}] ERR {etiqueta} {mensaje}".rstrip()
        self._escribir(texto)

    def warning(self, etiqueta: str, mensaje: str = ""):
        texto = f"[{self._timestamp()}] [{self.nombre}] WRN {etiqueta} {mensaje}".rstrip()
        self._escribir(texto)

    def info(self, mensaje: str):
        texto = f"[{self._timestamp()}] [{self.nombre}] INF {mensaje}"
        self._escribir(texto)

    def divider(self):
        self._escribir(f"[{self._timestamp()}] [{self.nombre}] " + "-" * 50)
