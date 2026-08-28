// =====================================================
// ELEMENTOS DEL DOM
// =====================================================

const fileInput =
    document.getElementById("fileInput");

const selectFileButton =
    document.getElementById("selectFile");

const uploadArea =
    document.getElementById("uploadArea");

const fileName =
    document.getElementById("fileName");

const convertButton =
    document.getElementById("convertButton");

const clientSelect =
    document.getElementById("client");

const conversionSelect =
    document.getElementById("conversion");

const status =
    document.getElementById("status");

const fileAnalysis =
    document.getElementById("fileAnalysis");

const fileAnalysisStatus =
    document.getElementById("fileAnalysisStatus");

const fileAnalysisDetails =
    document.getElementById("fileAnalysisDetails");


// =====================================================
// COLUMNAS
// =====================================================

const columnSearch =
    document.getElementById("columnSearch");

const selectAllColumnsButton =
    document.getElementById(
        "selectAllColumns"
    );

const deselectAllColumnsButton =
    document.getElementById(
        "deselectAllColumns"
    );

const columnSelection =
    document.getElementById(
        "columnSelection"
    );

const columnSelectionCount =
    document.getElementById(
        "columnSelectionCount"
    );


// =====================================================
// TRANSFORMACIONES
// =====================================================

const transformationsContainer =
    document.getElementById(
        "transformationsContainer"
    );

const addTransformationButton =
    document.getElementById(
        "addTransformationButton"
    );

const transformationForm =
    document.getElementById(
        "transformationForm"
    );

const transformationType =
    document.getElementById(
        "transformationType"
    );

const transformationColumns =
    document.getElementById(
        "transformationColumns"
    );

const transformationColumnsHelp =
    document.getElementById(
        "transformationColumnsHelp"
    );

const transformationOutput =
    document.getElementById(
        "transformationOutput"
    );

const cancelTransformationButton =
    document.getElementById(
        "cancelTransformationButton"
    );

const saveTransformationButton =
    document.getElementById(
        "saveTransformationButton"
    );

const transformationsList =
    document.getElementById(
        "transformationsList"
    );


// =====================================================
// ESTADO DE LA APLICACIÓN
// =====================================================

let selectedFile = null;

let uploadedFilename = null;

let excelAnalysis = null;

let selectedColumns = [];

let transformations = [];


// =====================================================
// CLIENTES
// =====================================================

async function loadClients() {

    try {

        const response = await fetch("/api/clients");

        if (!response.ok) {
            throw new Error(
                "No se pudieron cargar los clientes."
            );
        }

        const data = await response.json();

        console.log("Clientes recibidos:", data);

        /*
         * El backend puede devolver:
         *
         * [
         *   {
         *     "id": "demo",
         *     "name": "Cliente de prueba"
         *   }
         * ]
         *
         * o:
         *
         * {
         *   "clients": [...]
         * }
         */

        const clients = Array.isArray(data)
            ? data
            : (data.clients || []);

        clientSelect.innerHTML = `
            <option value="">
                Selecciona un cliente
            </option>
        `;

        for (const client of clients) {

            const option =
                document.createElement("option");

            option.value = client.id;

            option.textContent = client.name;

            clientSelect.appendChild(option);
        }

        if (clients.length === 0) {

            clientSelect.innerHTML = `
                <option value="">
                    No hay clientes configurados
                </option>
            `;
        }

    } catch (error) {

        console.error(
            "Error cargando clientes:",
            error
        );

        clientSelect.innerHTML = `
            <option value="">
                Error al cargar clientes
            </option>
        `;
    }
}


// =====================================================
// CAMBIO DE CLIENTE
// =====================================================

clientSelect.addEventListener(
    "change",
    async () => {

        const clientId =
            clientSelect.value;


        resetConversion();


        if (!clientId) {

            updateButton();

            return;
        }


        await loadConversions(
            clientId
        );
    }
);


// =====================================================
// CAMBIO DE CONVERSIÓN
// =====================================================

conversionSelect.addEventListener(
    "change",
    () => {

        updateButton();
    }
);


// =====================================================
// RESET CONVERSIÓN
// =====================================================

function resetConversion() {

    conversionSelect.innerHTML = `
        <option value="">
            Selecciona una conversión
        </option>
    `;


    conversionSelect.disabled =
        true;


    transformations = [];

    renderTransformations();

    updateButton();
}


// =====================================================
// CARGAR CONVERSIONES
// =====================================================

async function loadConversions(
    clientId
) {

    conversionSelect.innerHTML = `
        <option value="">
            Cargando conversiones...
        </option>
    `;


    conversionSelect.disabled =
        true;


    try {

        const response =
            await fetch(
                `/api/clients/${encodeURIComponent(
                    clientId
                )}/conversions`
            );


        if (!response.ok) {

            throw new Error(
                "No se pudieron cargar las conversiones."
            );
        }


        const data =
            await response.json();


        conversionSelect.innerHTML = `
            <option value="">
                Selecciona una conversión
            </option>
        `;


        for (
            const conversion
            of data.conversions
        ) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                conversion.id;


            option.textContent =
                conversion.name;


            conversionSelect.appendChild(
                option
            );
        }


        if (
            data.conversions.length === 0
        ) {

            conversionSelect.innerHTML = `
                <option value="">
                    No hay conversiones configuradas
                </option>
            `;

            conversionSelect.disabled =
                true;

        } else {

            conversionSelect.disabled =
                false;
        }


    } catch (error) {

        conversionSelect.innerHTML = `
            <option value="">
                Error al cargar conversiones
            </option>
        `;


        conversionSelect.disabled =
            true;


        console.error(error);
    }


    updateButton();
}


// =====================================================
// SELECCIÓN DE ARCHIVO
// =====================================================

selectFileButton.addEventListener(
    "click",
    () => {

        fileInput.click();
    }
);


fileInput.addEventListener(
    "change",
    () => {

        if (
            fileInput.files.length > 0
        ) {

            handleFile(
                fileInput.files[0]
            );
        }
    }
);


// =====================================================
// DRAG & DROP
// =====================================================

uploadArea.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        uploadArea.classList.add(
            "dragover"
        );
    }
);


uploadArea.addEventListener(
    "dragleave",
    () => {

        uploadArea.classList.remove(
            "dragover"
        );
    }
);


uploadArea.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        uploadArea.classList.remove(
            "dragover"
        );


        if (
            event.dataTransfer.files.length > 0
        ) {

            handleFile(
                event.dataTransfer.files[0]
            );
        }
    }
);


// =====================================================
// MANEJAR ARCHIVO
// =====================================================

async function handleFile(file) {

    const extension =
        file.name
            .substring(
                file.name.lastIndexOf(".")
            )
            .toLowerCase();


    if (
        extension !== ".xlsx"
    ) {

        showStatus(
            "El archivo debe ser un Excel .xlsx.",
            "error"
        );

        return;
    }


    selectedFile = file;

    uploadedFilename = null;

    excelAnalysis = null;

    selectedColumns = [];

    transformations = [];


    fileName.textContent =
        `Archivo seleccionado: ${file.name}`;


    fileAnalysis.classList.add(
        "hidden"
    );


    renderTransformations();

    updateButton();


    await uploadFile(file);
}


// =====================================================
// SUBIR ARCHIVO
// =====================================================

async function uploadFile(file) {

    showStatus(
        "Subiendo archivo...",
        "loading"
    );


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        const response =
            await fetch(
                "/api/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "No se pudo subir el archivo."
            );
        }


        uploadedFilename =
            data.filename;


        showStatus(
            "Excel subido. Analizando archivo...",
            "loading"
        );


        await analyzeFile(
            uploadedFilename
        );


    } catch (error) {

        uploadedFilename = null;

        excelAnalysis = null;

        selectedColumns = [];

        transformations = [];


        showStatus(
            `Error: ${error.message}`,
            "error"
        );


        console.error(error);


        updateButton();
    }
}


// =====================================================
// ANALIZAR EXCEL
// =====================================================

async function analyzeFile(
    filename
) {

    try {

        const response =
            await fetch(
                `/api/analyze/${encodeURIComponent(
                    filename
                )}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "No se pudo analizar el Excel."
            );
        }


        excelAnalysis =
            data;


        showAnalysis(
            data
        );


        updateButton();


    } catch (error) {

        excelAnalysis = null;

        selectedColumns = [];

        transformations = [];


        showStatus(
            `Error al analizar el Excel: ${error.message}`,
            "error"
        );


        console.error(error);


        updateButton();
    }
}


// =====================================================
// MOSTRAR ANÁLISIS
// =====================================================

function showAnalysis(data) {

    const sheets =
        data.sheets || [];


    if (
        sheets.length === 0
    ) {

        showStatus(
            "El Excel no contiene ninguna hoja.",
            "error"
        );


        fileAnalysis.classList.add(
            "hidden"
        );


        return;
    }


    const totalRows =
        sheets.reduce(
            (total, sheet) =>
                total + sheet.rows,
            0
        );


    const totalColumns =
        sheets.reduce(
            (total, sheet) =>
                total + sheet.columns,
            0
        );


    fileAnalysis.classList.remove(
        "hidden"
    );


    fileAnalysisStatus.textContent =
        "✓ Excel analizado correctamente";


    fileAnalysisDetails.textContent =
        `${sheets.length} hoja(s) · ` +
        `${totalRows} filas · ` +
        `${totalColumns} columna(s)`;


    const firstSheet =
        sheets[0];


    const columns =
        firstSheet.column_details || [];


    selectedColumns =
        columns
            .map(
                column =>
                    column.name
            )
            .filter(
                name =>
                    name &&
                    !name.startsWith(
                        "Unnamed:"
                    )
            );


    renderColumns(
        columns
    );


    updateColumnSelectionCount();


    transformations = [];

    renderTransformations();


    showStatus(
        "",
        ""
    );


    console.log(
        "Análisis del Excel:",
        data
    );
}


// =====================================================
// MOSTRAR COLUMNAS
// =====================================================

function renderColumns(
    columns
) {

    columnSelection.innerHTML =
        "";


    const searchTerm =
        columnSearch.value
            .trim()
            .toLowerCase();


    const filteredColumns =
        columns.filter(
            column => {

                const name =
                    String(
                        column.name
                    );


                if (
                    name.startsWith(
                        "Unnamed:"
                    )
                ) {

                    return false;
                }


                return name
                    .toLowerCase()
                    .includes(
                        searchTerm
                    );
            }
        );


    if (
        filteredColumns.length === 0
    ) {

        columnSelection.innerHTML = `
            <div class="column-option">
                No se encontraron columnas.
            </div>
        `;

        return;
    }


    for (
        const column
        of filteredColumns
    ) {

        const name =
            String(
                column.name
            );


        const label =
            document.createElement(
                "label"
            );


        label.className =
            "column-option";


        const checkbox =
            document.createElement(
                "input"
            );


        checkbox.type =
            "checkbox";


        checkbox.value =
            name;


        checkbox.checked =
            selectedColumns.includes(
                name
            );


        checkbox.addEventListener(
            "change",
            () => {

                if (
                    checkbox.checked
                ) {

                    if (
                        !selectedColumns.includes(
                            name
                        )
                    ) {

                        selectedColumns.push(
                            name
                        );
                    }

                } else {

                    selectedColumns =
                        selectedColumns.filter(
                            columnName =>
                                columnName !==
                                name
                        );
                }


                updateColumnSelectionCount();

                updateButton();
            }
        );


        const text =
            document.createElement(
                "span"
            );


        text.textContent =
            name;


        label.appendChild(
            checkbox
        );


        label.appendChild(
            text
        );


        columnSelection.appendChild(
            label
        );
    }
}


// =====================================================
// BUSCADOR
// =====================================================

columnSearch.addEventListener(
    "input",
    () => {

        if (!excelAnalysis) {
            return;
        }


        const firstSheet =
            excelAnalysis.sheets[0];


        const columns =
            firstSheet.column_details || [];


        renderColumns(
            columns
        );
    }
);


// =====================================================
// SELECCIONAR TODAS
// =====================================================

selectAllColumnsButton.addEventListener(
    "click",
    () => {

        if (!excelAnalysis) {
            return;
        }


        const columns =
            excelAnalysis
                .sheets[0]
                .column_details || [];


        selectedColumns =
            columns
                .map(
                    column =>
                        String(
                            column.name
                        )
                )
                .filter(
                    name =>
                        name &&
                        !name.startsWith(
                            "Unnamed:"
                        )
                );


        renderColumns(
            columns
        );


        updateColumnSelectionCount();

        updateButton();
    }
);


// =====================================================
// DESELECCIONAR TODAS
// =====================================================

deselectAllColumnsButton.addEventListener(
    "click",
    () => {

        if (!excelAnalysis) {
            return;
        }


        selectedColumns = [];


        const columns =
            excelAnalysis
                .sheets[0]
                .column_details || [];


        renderColumns(
            columns
        );


        updateColumnSelectionCount();

        updateButton();
    }
);


// =====================================================
// CONTADOR
// =====================================================

function updateColumnSelectionCount() {

    const total =
        getAvailableColumns().length;


    columnSelectionCount.textContent =
        `${selectedColumns.length} ` +
        `de ${total} columnas seleccionadas`;
}


// =====================================================
// OBTENER COLUMNAS DISPONIBLES
// =====================================================

function getAvailableColumns() {

    if (!excelAnalysis) {
        return [];
    }


    const firstSheet =
        excelAnalysis.sheets[0];


    return (
        firstSheet.column_details || []
    )
        .map(
            column =>
                String(
                    column.name
                )
        )
        .filter(
            name =>
                name &&
                !name.startsWith(
                    "Unnamed:"
                )
        );
}


// =====================================================
// MOSTRAR TRANSFORMACIONES
// =====================================================

function renderTransformations() {

    if (
        !excelAnalysis
    ) {

        transformationsContainer.classList.add(
            "hidden"
        );

        return;
    }


    transformationsContainer.classList.remove(
        "hidden"
    );


    transformationsList.innerHTML =
        "";


    if (
        transformations.length === 0
    ) {

        transformationsList.innerHTML = `
            <p class="transformation-help">
                Todavía no hay transformaciones.
            </p>
        `;

        return;
    }


    for (
        let index = 0;
        index < transformations.length;
        index++
    ) {

        const transformation =
            transformations[index];


        const card =
            document.createElement(
                "div"
            );


        card.className =
            "transformation-card";


        const header =
            document.createElement(
                "div"
            );


        header.className =
            "transformation-card-header";


        const title =
            document.createElement(
                "div"
            );


        title.className =
            "transformation-card-title";


        title.textContent =
            transformation.output;


        const removeButton =
            document.createElement(
                "button"
            );


        removeButton.type =
            "button";


        removeButton.className =
            "remove-transformation-button";


        removeButton.textContent =
            "Eliminar";


        removeButton.addEventListener(
            "click",
            () => {

                transformations.splice(
                    index,
                    1
                );


                renderTransformations();

                updateButton();
            }
        );


        header.appendChild(
            title
        );


        header.appendChild(
            removeButton
        );


        const operation =
            document.createElement(
                "div"
            );


        operation.className =
            "transformation-card-operation";


        operation.textContent =
            `${getOperationLabel(
                transformation.operation
            )}: ` +
            `${transformation.columns.join(
                " + "
            )}`;


        card.appendChild(
            header
        );


        card.appendChild(
            operation
        );


        transformationsList.appendChild(
            card
        );
    }
}


// =====================================================
// NOMBRE DE OPERACIÓN
// =====================================================

function getOperationLabel(
    operation
) {

    const labels = {

        sum: "Sumar",

        subtract: "Restar",

        multiply: "Multiplicar",

        divide: "Dividir"

    };


    return (
        labels[operation] ||
        operation
    );
}


// =====================================================
// AÑADIR TRANSFORMACIÓN
// =====================================================

addTransformationButton.addEventListener(
    "click",
    () => {

        transformationForm.classList.remove(
            "hidden"
        );


        renderTransformationColumns();


        transformationOutput.focus();
    }
);


// =====================================================
// CANCELAR TRANSFORMACIÓN
// =====================================================

cancelTransformationButton.addEventListener(
    "click",
    () => {

        resetTransformationForm();
    }
);


// =====================================================
// CAMBIAR TIPO
// =====================================================

transformationType.addEventListener(
    "change",
    () => {

        renderTransformationColumns();
    }
);


// =====================================================
// MOSTRAR COLUMNAS PARA TRANSFORMACIÓN
// =====================================================

function renderTransformationColumns() {

    transformationColumns.innerHTML =
        "";


    if (!excelAnalysis) {
        return;
    }


    const numericColumns =
        getNumericColumns();


    if (
        numericColumns.length === 0
    ) {

        transformationColumns.innerHTML = `
            <p class="transformation-help">
                No se han detectado columnas numéricas compatibles.
            </p>
        `;

        return;
    }


    for (
        const column
        of numericColumns
    ) {

        const label =
            document.createElement(
                "label"
            );


        label.className =
            "transformation-column-option";


        const checkbox =
            document.createElement(
                "input"
            );


        checkbox.type =
            "checkbox";


        checkbox.value =
            column.name;


        const text =
            document.createElement(
                "span"
            );


        text.textContent =
            column.name;


        label.appendChild(
            checkbox
        );


        label.appendChild(
            text
        );


        transformationColumns.appendChild(
            label
        );
    }


    transformationColumnsHelp.textContent =
        "Solo se muestran columnas numéricas, compatibles con esta operación.";
}


// =====================================================
// DETECTAR COLUMNAS NUMÉRICAS
// =====================================================

function getNumericColumns() {

    if (!excelAnalysis) {
        return [];
    }


    const firstSheet =
        excelAnalysis.sheets[0];


    const columns =
        firstSheet.column_details || [];


    return columns.filter(
        column => {

            const dtype =
                String(
                    column.dtype || ""
                ).toLowerCase();


            return (
                dtype.includes("int") ||
                dtype.includes("float") ||
                dtype.includes("number")
            );
        }
    );
}


// =====================================================
// GUARDAR TRANSFORMACIÓN
// =====================================================

saveTransformationButton.addEventListener(
    "click",
    () => {

        const operation =
            transformationType.value;


        const checkboxes =
            transformationColumns
                .querySelectorAll(
                    "input[type='checkbox']:checked"
                );


        const columns =
            Array.from(
                checkboxes
            )
                .map(
                    checkbox =>
                        checkbox.value
                );


        const output =
            transformationOutput.value
                .trim();


        if (
            columns.length < 2
        ) {

            showStatus(
                "Selecciona al menos dos columnas para la transformación.",
                "error"
            );

            return;
        }


        if (!output) {

            showStatus(
                "Escribe el nombre de la nueva columna.",
                "error"
            );

            transformationOutput.focus();

            return;
        }


        if (
            getAvailableColumns()
                .includes(output)
        ) {

            showStatus(
                "El nombre de la nueva columna ya existe.",
                "error"
            );

            transformationOutput.focus();

            return;
        }


        if (
            transformations.some(
                transformation =>
                    transformation.output ===
                    output
            )
        ) {

            showStatus(
                "Ya existe una transformación con ese nombre.",
                "error"
            );

            transformationOutput.focus();

            return;
        }


        transformations.push({

            operation: operation,

            columns: columns,

            output: output

        });


        resetTransformationForm();


        renderTransformations();

        updateButton();


        showStatus(
            "Transformación añadida correctamente.",
            "success"
        );
    }
);


// =====================================================
// RESET FORMULARIO TRANSFORMACIÓN
// =====================================================

function resetTransformationForm() {

    transformationForm.classList.add(
        "hidden"
    );


    transformationOutput.value =
        "";


    transformationColumns.innerHTML =
        "";


    transformationType.value =
        "sum";
}


// =====================================================
// BOTÓN CONVERTIR
// =====================================================

function updateButton() {

    const clientSelected =
        clientSelect.value !== "";


    const conversionSelected =
        conversionSelect.value !== "";


    const fileSelected =
        selectedFile !== null;


    const fileAnalyzed =
        excelAnalysis !== null;


    const columnsSelected =
        selectedColumns.length > 0;


    convertButton.disabled = !(
        clientSelected &&
        conversionSelected &&
        fileSelected &&
        fileAnalyzed &&
        columnsSelected
    );
}


// =====================================================
// CONVERTIR
// =====================================================

convertButton.addEventListener(
    "click",
    async () => {

        if (
            !selectedFile ||
            !clientSelect.value ||
            !conversionSelect.value ||
            selectedColumns.length === 0
        ) {

            return;
        }


        convertButton.disabled =
            true;


        convertButton.textContent =
            "Convirtiendo...";


        showStatus(
            "Preparando la conversión...",
            "loading"
        );


        try {

            // -----------------------------------------
            // 1. SUBIR ARCHIVO
            // -----------------------------------------

            const formData =
                new FormData();


            formData.append(
                "file",
                selectedFile
            );


            const uploadResponse =
                await fetch(
                    "/api/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (
                !uploadResponse.ok
            ) {

                const errorData =
                    await uploadResponse
                        .json()
                        .catch(
                            () => null
                        );


                throw new Error(
                    errorData?.detail ||
                    "No se pudo subir el archivo."
                );
            }


            const uploadData =
                await uploadResponse.json();


            // -----------------------------------------
            // 2. CONVERTIR
            // -----------------------------------------

            showStatus(
                "Convirtiendo archivo...",
                "loading"
            );


            const clientId =
                clientSelect.value;


            const conversionId =
                conversionSelect.value;


            const selectedColumnsParam =
                encodeURIComponent(
                    JSON.stringify(
                        selectedColumns
                    )
                );


            const transformationsParam =
                encodeURIComponent(
                    JSON.stringify(
                        transformations
                    )
                );


            const convertUrl =
                `/api/convert?` +
                `filename=${encodeURIComponent(
                    uploadData.filename
                )}` +
                `&client_id=${encodeURIComponent(
                    clientId
                )}` +
                `&conversion_id=${encodeURIComponent(
                    conversionId
                )}` +
                `&selected_columns=${selectedColumnsParam}` +
                `&transformations=${transformationsParam}`;


            const convertResponse =
                await fetch(
                    convertUrl,
                    {
                        method: "POST"
                    }
                );


            if (
                !convertResponse.ok
            ) {

                const errorData =
                    await convertResponse
                        .json()
                        .catch(
                            () => null
                        );


                throw new Error(
                    errorData?.detail ||
                    "No se pudo convertir el archivo."
                );
            }


            // -----------------------------------------
            // 3. DESCARGAR
            // -----------------------------------------

            const blob =
                await convertResponse.blob();


            const downloadUrl =
                window.URL.createObjectURL(
                    blob
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                downloadUrl;


            link.download =
                `CONTASOL_${uploadData.filename}`;


            document.body.appendChild(
                link
            );


            link.click();


            link.remove();


            window.URL.revokeObjectURL(
                downloadUrl
            );


            showStatus(
                "✓ Conversión completada. El archivo se ha descargado.",
                "success"
            );


        } catch (error) {

            console.error(error);


            showStatus(
                `Error: ${error.message}`,
                "error"
            );


        } finally {

            convertButton.disabled =
                false;


            convertButton.textContent =
                "Convertir a CONTASOL";


            updateButton();
        }
    }
);


// =====================================================
// MENSAJES
// =====================================================

function showStatus(
    message,
    type
) {

    if (!message) {

        status.classList.add(
            "hidden"
        );


        status.textContent =
            "";


        return;
    }


    status.classList.remove(
        "hidden"
    );


    status.textContent =
        message;


    status.className =
        "status";


    if (type) {

        status.classList.add(
            type
        );
    }
}


// =====================================================
// INICIO
// =====================================================

loadClients();