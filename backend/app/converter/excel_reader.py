from pathlib import Path
from typing import Any

import pandas as pd


class ExcelReader:
    """Lee y analiza archivos Excel."""

    PREVIEW_ROWS = 25

    def __init__(self, file_path: Path):
        self.file_path = file_path

    # =================================================
    # HOJAS
    # =================================================

    def get_sheet_names(self) -> list[str]:
        """Devuelve los nombres de las hojas del Excel."""

        excel_file = pd.ExcelFile(
            self.file_path
        )

        return excel_file.sheet_names

    # =================================================
    # DETECTAR CABECERA
    # =================================================

    def detect_header_row(
        self,
        sheet_name: str,
        max_rows: int = 20,
    ) -> int:
        """
        Detecta automáticamente la fila que contiene
        los nombres de las columnas.

        Devuelve el índice de la fila empezando
        desde 0.
        """

        raw_dataframe = pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
            header=None,
            nrows=max_rows,
        )

        if raw_dataframe.empty:
            return 0

        best_row = 0
        best_score = -1

        for index, row in raw_dataframe.iterrows():

            values = [
                value
                for value in row.tolist()
                if not pd.isna(value)
                and str(value).strip() != ""
            ]

            if not values:
                continue

            non_empty_count = len(values)

            text_count = 0

            for value in values:

                if isinstance(value, str):

                    if value.strip():
                        text_count += 1

            score = (
                non_empty_count * 10
                + text_count * 5
            )

            if (
                non_empty_count >= 2
                and text_count > 0
                and score > best_score
            ):

                best_score = score
                best_row = index

        return best_row

    # =================================================
    # LIMPIAR DATAFRAME
    # =================================================

    def _clean_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Limpia un DataFrame después de leerlo.
        """

        # ---------------------------------------------
        # Eliminar columnas completamente vacías
        # ---------------------------------------------

        dataframe = dataframe.dropna(
            axis=1,
            how="all",
        )

        # ---------------------------------------------
        # Limpiar nombres de columnas
        # ---------------------------------------------

        cleaned_columns = []

        for column in dataframe.columns:

            column_name = str(
                column
            ).strip()

            cleaned_columns.append(
                column_name
            )

        dataframe.columns = (
            cleaned_columns
        )

        # ---------------------------------------------
        # Eliminar filas completamente vacías
        # ---------------------------------------------

        dataframe = dataframe.dropna(
            axis=0,
            how="all",
        )

        return dataframe

    # =================================================
    # LEER HOJA
    # =================================================

    def read_sheet(
        self,
        sheet_name: str,
    ) -> pd.DataFrame:
        """
        Lee una hoja completa detectando
        automáticamente la fila de cabeceras.
        """

        header_row = self.detect_header_row(
            sheet_name
        )

        dataframe = pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
            header=header_row,
        )

        return self._clean_dataframe(
            dataframe
        )

    # =================================================
    # CONVERTIR VALOR PARA JSON
    # =================================================

    def _serialize_value(
        self,
        value: Any,
    ) -> Any:
        """
        Convierte valores de pandas/numpy a valores
        compatibles con JSON.
        """

        if pd.isna(value):

            return ""

        if hasattr(
            value,
            "item",
        ):

            try:

                value = value.item()

            except (
                ValueError,
                AttributeError,
            ):

                value = str(value)

        elif not isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
                type(None),
            ),
        ):

            value = str(value)

        return value

    # =================================================
    # CONVERTIR FILA
    # =================================================

    def _serialize_row(
        self,
        row: pd.Series,
        row_number: int,
        columns: list[str],
    ) -> dict[str, Any]:
        """
        Convierte una fila en un diccionario preparado
        para enviarlo al frontend.
        """

        row_data = {
            "_row_number": row_number
        }

        for column in columns:

            value = row[column]

            row_data[
                str(column)
            ] = self._serialize_value(
                value
            )

        return row_data

    # =================================================
    # PREVIEW PAGINADO
    # =================================================

    def get_preview(
        self,
        sheet_name: str,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        """
        Devuelve una página concreta de una hoja.

        page:
            Número de página empezando en 1.

        page_size:
            Número de filas por página.
        """

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = self.PREVIEW_ROWS

        # Limitar para evitar peticiones exageradas
        page_size = min(
            page_size,
            100,
        )

        header_row = self.detect_header_row(
            sheet_name
        )

        dataframe = self.read_sheet(
            sheet_name
        )

        total_rows = len(
            dataframe
        )

        total_pages = max(
            1,
            (
                total_rows +
                page_size -
                1
            )
            // page_size,
        )

        # Si piden una página inexistente,
        # devolvemos la última.
        if page > total_pages:
            page = total_pages

        start_position = (
            page - 1
        ) * page_size

        end_position = min(
            start_position +
            page_size,
            total_rows,
        )

        page_dataframe = (
            dataframe
            .iloc[
                start_position:end_position
            ]
        )

        columns = [
            str(column)
            for column
            in dataframe.columns
        ]

        rows = []

        for index, row in (
            page_dataframe.iterrows()
        ):

            # -----------------------------------------
            # Número real de fila del Excel
            #
            # índice dataframe + fila cabecera + 2
            # -----------------------------------------

            row_number = (
                int(index)
                + header_row
                + 2
            )

            rows.append(
                self._serialize_row(
                    row,
                    row_number,
                    columns,
                )
            )

        return {
            "sheet": sheet_name,
            "page": page,
            "page_size": page_size,
            "total_rows": total_rows,
            "total_pages": total_pages,
            "start_row": (
                rows[0]["_row_number"]
                if rows
                else None
            ),
            "end_row": (
                rows[-1]["_row_number"]
                if rows
                else None
            ),
            "column_names": columns,
            "rows": rows,
        }

    # =================================================
    # ANALIZAR
    # =================================================

    def analyze(self) -> dict:
        """Analiza la estructura completa del Excel."""

        sheets = []

        for sheet_name in self.get_sheet_names():

            dataframe = self.read_sheet(
                sheet_name
            )

            header_row = (
                self.detect_header_row(
                    sheet_name
                )
            )

            # -----------------------------------------
            # Información de columnas
            # -----------------------------------------

            columns = []

            for column in dataframe.columns:

                columns.append(
                    {
                        "name": str(column),
                        "dtype": str(
                            dataframe[column].dtype
                        ),
                        "empty": bool(
                            dataframe[column]
                            .isna()
                            .all()
                        ),
                    }
                )

            # -----------------------------------------
            # Nombres de columnas
            # -----------------------------------------

            column_names = [
                str(column)
                for column
                in dataframe.columns
            ]

            # -----------------------------------------
            # Preview inicial
            # -----------------------------------------

            preview_result = self.get_preview(
                sheet_name=sheet_name,
                page=1,
                page_size=self.PREVIEW_ROWS,
            )

            # -----------------------------------------
            # Información de la hoja
            # -----------------------------------------

            sheets.append(
                {
                    "name": sheet_name,
                    "header_row": (
                        header_row + 1
                    ),
                    "rows": len(
                        dataframe
                    ),
                    "columns": len(
                        dataframe.columns
                    ),
                    "column_names": (
                        column_names
                    ),
                    "column_details": (
                        columns
                    ),
                    "preview": (
                        preview_result["rows"]
                    ),
                }
            )

        return {
            "filename": self.file_path.name,
            "sheets": sheets,
        }