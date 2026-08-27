from pathlib import Path

import pandas as pd


class ExcelReader:
    """Lee y analiza archivos Excel."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def get_sheet_names(self) -> list[str]:
        """Devuelve los nombres de las hojas del Excel."""

        excel_file = pd.ExcelFile(self.file_path)

        return excel_file.sheet_names

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Lee una hoja concreta del Excel."""

        return pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
        )

    def analyze(self) -> dict:
        """Analiza la estructura completa del Excel."""

        sheets = []

        for sheet_name in self.get_sheet_names():
            dataframe = self.read_sheet(sheet_name)

            columns = []

            for column in dataframe.columns:
                columns.append(
                    {
                        "name": str(column),
                        "dtype": str(dataframe[column].dtype),
                        "empty": bool(dataframe[column].isna().all()),
                    }
                )

            preview = dataframe.head(5).fillna("").to_dict(
                orient="records"
            )

            sheets.append(
                {
                    "name": sheet_name,
                    "rows": len(dataframe),
                    "columns": len(dataframe.columns),
                    "column_details": columns,
                    "preview": preview,
                }
            )

        return {
            "filename": self.file_path.name,
            "sheets": sheets,
        }