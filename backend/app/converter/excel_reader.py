from pathlib import Path

import pandas as pd


class ExcelReader:
    """Lee y analiza archivos Excel."""

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

            # -----------------------------------------
            # Número de celdas con contenido
            # -----------------------------------------

            non_empty_count = len(values)

            # -----------------------------------------
            # Penalizar filas donde predominan números
            #
            # Una cabecera normalmente contiene texto.
            # -----------------------------------------

            text_count = 0

            for value in values:

                if isinstance(value, str):
                    if value.strip():
                        text_count += 1

            # -----------------------------------------
            # Puntuación
            # -----------------------------------------

            score = (
                non_empty_count * 10
                + text_count * 5
            )

            # -----------------------------------------
            # Preferimos una fila que tenga al menos
            # dos valores y que contenga texto.
            # -----------------------------------------

            if (
                non_empty_count >= 2
                and text_count > 0
                and score > best_score
            ):

                best_score = score
                best_row = index

        return best_row

    # =================================================
    # LEER HOJA
    # =================================================

    def read_sheet(
        self,
        sheet_name: str,
    ) -> pd.DataFrame:
        """
        Lee una hoja concreta detectando
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
    # ANALIZAR
    # =================================================

    def analyze(self) -> dict:
        """Analiza la estructura completa del Excel."""

        sheets = []

        for sheet_name in self.get_sheet_names():

            dataframe = self.read_sheet(
                sheet_name
            )

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
            # Preview
            # -----------------------------------------

            preview = (
                dataframe
                .head(5)
                .fillna("")
                .to_dict(
                    orient="records"
                )
            )

            # -----------------------------------------
            # Información de la hoja
            # -----------------------------------------

            header_row = (
                self.detect_header_row(
                    sheet_name
                )
            )

            sheets.append(
                {
                    "name": sheet_name,
                    "header_row": header_row + 1,
                    "rows": len(dataframe),
                    "columns": len(
                        dataframe.columns
                    ),
                    "column_details": columns,
                    "preview": preview,
                }
            )

        return {
            "filename": self.file_path.name,
            "sheets": sheets,
        }