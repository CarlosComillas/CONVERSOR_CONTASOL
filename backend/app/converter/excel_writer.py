from pathlib import Path
from typing import Any

import pandas as pd


class ExcelWriter:
    """
    Genera el Excel final a partir de los datos transformados.
    """

    def write(
        self,
        rows: list[dict[str, Any]],
        output_path: Path,
    ) -> Path:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        dataframe = pd.DataFrame(rows)

        dataframe.to_excel(
            output_path,
            index=False
        )

        return output_path