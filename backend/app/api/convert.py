import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.converter.excel_writer import ExcelWriter
from backend.app.converter.mapper import ExcelMapper
from backend.app.converter.transformer import DataTransformer
from backend.app.converter.validator import DataValidator
from backend.app.services.config_manager import ConfigManager


router = APIRouter(
    prefix="/api",
    tags=["Conversion"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

CLIENTS_CONFIG_DIR = BASE_DIR / "config" / "clients"

config_manager = ConfigManager(
    CLIENTS_CONFIG_DIR
)


@router.post("/convert")
def convert_excel(
    filename: str,
    client_id: str,
    conversion_id: str,
    selected_columns: str | None = None,
    transformations: str | None = None,
    selected_rows: str | None = None,
):
    """
    Convierte un Excel utilizando la configuración
    del cliente y de la conversión seleccionada.

    La selección manual de columnas, filas y
    transformaciones realizada desde la interfaz
    tiene prioridad sobre la configuración guardada.

    selected_rows tiene este formato:

    {
        "Hoja1": [2, 3, 5],
        "Hoja2": [4, 8]
    }

    Las filas utilizan el número real de fila
    del Excel.
    """

    # =================================================
    # 1. COMPROBAR CLIENTE
    # =================================================

    try:

        config_manager.load_client(
            client_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe el cliente: "
                f"{client_id}"
            ),
        )


    # =================================================
    # 2. CARGAR CONVERSIÓN
    # =================================================

    try:

        conversion = (
            config_manager.load_conversion(
                client_id,
                conversion_id,
            )
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No existe la conversión "
                f"'{conversion_id}' para el "
                f"cliente '{client_id}'."
            ),
        )


    # =================================================
    # 3. COMPROBAR EXCEL
    # =================================================

    input_path = (
        INPUT_DIR /
        Path(filename).name
    )

    if not input_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "No se encontró el archivo Excel."
            ),
        )


    if input_path.suffix.lower() not in {
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser un Excel "
                ".xlsx o .xls."
            ),
        )


    # =================================================
    # 4. NOMBRE DEL ARCHIVO DE SALIDA
    # =================================================

    output_filename = (
        f"CONTASOL_{client_id}_"
        f"{conversion_id}_"
        f"{input_path.stem}.xlsx"
    )

    output_path = (
        OUTPUT_DIR /
        output_filename
    )


    try:

        # =================================================
        # 5. LEER EXCEL
        # =================================================

        excel_file = pd.ExcelFile(
            input_path
        )

        sheet_names = (
            excel_file.sheet_names
        )

        if not sheet_names:

            raise HTTPException(
                status_code=400,
                detail=(
                    "El Excel no contiene hojas."
                ),
            )


        # =================================================
        # 6. OBTENER COLUMNAS
        # =================================================

        configured_columns = (
            conversion.get(
                "selected_columns"
            )
        )

        selected_columns_list = None


        if selected_columns is not None:

            try:

                selected_columns_list = (
                    json.loads(
                        selected_columns
                    )
                )

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de columnas "
                        "no tiene un formato válido."
                    ),
                )


            if not isinstance(
                selected_columns_list,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de columnas "
                        "debe ser una lista."
                    ),
                )


            if not all(
                isinstance(
                    column,
                    str,
                )
                for column
                in selected_columns_list
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Los nombres de las columnas "
                        "deben ser texto."
                    ),
                )


        else:

            selected_columns_list = (
                configured_columns
            )


        # =================================================
        # 7. OBTENER FILAS SELECCIONADAS
        # =================================================

        selected_rows_config = None


        if selected_rows is not None:

            try:

                selected_rows_config = (
                    json.loads(
                        selected_rows
                    )
                )

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de filas "
                        "no tiene un formato válido."
                    ),
                )


            if not isinstance(
                selected_rows_config,
                dict,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "La selección de filas "
                        "debe ser un objeto."
                    ),
                )


            for (
                sheet_name,
                rows
            ) in selected_rows_config.items():

                if not isinstance(
                    sheet_name,
                    str,
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "El nombre de la hoja "
                            "debe ser texto."
                        ),
                    )


                if not isinstance(
                    rows,
                    list,
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Las filas seleccionadas "
                            "deben ser una lista."
                        ),
                    )


                if not all(
                    isinstance(
                        row,
                        int,
                    )
                    for row
                    in rows
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Los números de fila "
                            "deben ser enteros."
                        ),
                    )


        # =================================================
        # 8. OBTENER MAPPING
        # =================================================

        mapping = conversion.get(
            "mapping",
            {},
        )


        # =================================================
        # 9. CONFIGURACIÓN DE VALIDACIÓN
        # =================================================

        validation_config = (
            conversion.get(
                "validation",
                {},
            )
        )

        required_fields = (
            validation_config.get(
                "required_fields",
                [],
            )
        )


        # =================================================
        # 10. OBTENER TRANSFORMACIONES
        # =================================================

        configured_transformations = (
            conversion.get(
                "transformations",
                {}
            )
        )


        if isinstance(
            configured_transformations,
            dict,
        ):

            transformation_config = (
                configured_transformations.copy()
            )

        else:

            transformation_config = {}


        # =================================================
        # 11. TRANSFORMACIONES DE LA INTERFAZ
        # =================================================

        if transformations is not None:

            try:

                manual_transformations = (
                    json.loads(
                        transformations
                    )
                )

            except json.JSONDecodeError:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Las transformaciones "
                        "no tienen un formato válido."
                    ),
                )


            if not isinstance(
                manual_transformations,
                list,
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Las transformaciones "
                        "deben ser una lista."
                    ),
                )


            transformation_config[
                "_operations"
            ] = manual_transformations


        # =================================================
        # 12. CONVERTIR HOJAS
        # =================================================
        #
        # Actualmente la conversión utiliza
        # la primera hoja del Excel.
        #
        # La estructura de selected_rows ya está
        # preparada para trabajar con múltiples hojas.
        #
        # =================================================

        first_sheet_name = (
            sheet_names[0]
        )


        dataframe = pd.read_excel(
            input_path,
            sheet_name=first_sheet_name,
        )


        # =================================================
        # 13. FILTRAR FILAS
        # =================================================

        if (
            selected_rows_config is not None
            and first_sheet_name
            in selected_rows_config
        ):

            requested_rows = (
                selected_rows_config[
                    first_sheet_name
                ]
            )

            if requested_rows:

                # El visor utiliza números de fila
                # empezando en 1.
                #
                # pandas utiliza índices empezando
                # en 0.
                #
                # Por eso convertimos:
                #
                # Excel fila 2 -> pandas índice 1

                dataframe = (
                    dataframe
                    .copy()
                )

                dataframe[
                    "_original_excel_row"
                ] = (
                    dataframe.index + 2
                )

                dataframe = (
                    dataframe[
                        dataframe[
                            "_original_excel_row"
                        ].isin(
                            requested_rows
                        )
                    ]
                )

                dataframe = (
                    dataframe.drop(
                        columns=[
                            "_original_excel_row"
                        ]
                    )
                )


        # =================================================
        # 14. VALIDAR COLUMNAS
        # =================================================

        if selected_columns_list is not None:

            missing_columns = [
                column
                for column
                in selected_columns_list
                if column
                not in dataframe.columns
            ]

            if missing_columns:

                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": (
                            "Algunas columnas "
                            "seleccionadas no existen "
                            "en el Excel."
                        ),
                        "missing_columns": (
                            missing_columns
                        ),
                    },
                )


        # =================================================
        # 15. CONVERTIR A RECORDS
        # =================================================

        rows = (
            dataframe
            .to_dict(
                orient="records"
            )
        )


        # =================================================
        # 16. MAPEAR
        # =================================================

        mapper = ExcelMapper(
            mapping=mapping,
            selected_columns=(
                selected_columns_list
            ),
        )

        mapped_rows = (
            mapper.map_rows(
                rows
            )
        )


        # =================================================
        # 17. TRANSFORMAR
        # =================================================

        transformer = DataTransformer(
            transformations=(
                transformation_config
            )
        )

        transformed_rows = (
            transformer.transform_rows(
                mapped_rows
            )
        )


        # =================================================
        # 18. VALIDAR
        # =================================================

        validator = DataValidator(
            required_fields=(
                required_fields
            )
        )

        validation_result = (
            validator.validate_rows(
                transformed_rows
            )
        )


        if not validation_result[
            "valid"
        ]:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "El Excel contiene "
                        "errores de validación."
                    ),
                    "validation": (
                        validation_result
                    ),
                },
            )


        # =================================================
        # 19. GENERAR EXCEL
        # =================================================

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        writer = ExcelWriter()

        writer.write(
            transformed_rows,
            output_path,
        )


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Error durante la conversión: "
                f"{error}"
            ),
        )


    # =================================================
    # 20. DESCARGAR RESULTADO
    # =================================================

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )