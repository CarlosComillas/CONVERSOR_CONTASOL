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
    document.getElementById("selectAllColumns");

const deselectAllColumnsButton =
    document.getElementById("deselectAllColumns");

const removeUnselectedColumnsButton =
    document.getElementById(
        "removeUnselectedColumns"
    );

const columnSelection =
    document.getElementById("columnSelection");

const columnSelectionCount =
    document.getElementById("columnSelectionCount");


// =====================================================
// VISOR
// =====================================================

const excelViewer =
    document.getElementById("excelViewer");

const viewerDetails =
    document.getElementById("viewerDetails");

const viewerSheet =
    document.getElementById("viewerSheet");

const excelTable =
    document.getElementById("excelTable");

const excelTableHead =
    document.getElementById("excelTableHead");

const excelTableBody =
    document.getElementById("excelTableBody");

const selectAllRowsButton =
    document.getElementById("selectAllRows");

const deselectAllRowsButton =
    document.getElementById("deselectAllRows");

const rowSelectionCount =
    document.getElementById("rowSelectionCount");

const viewerPagination =
    document.getElementById("viewerPagination");

const previousPageButton =
    document.getElementById("previousPage");

const nextPageButton =
    document.getElementById("nextPage");

const currentPageElement =
    document.getElementById("currentPage");


// =====================================================
// TRANSFORMACIONES
// =====================================================

const transformationsContainer =
    document.getElementById("transformationsContainer");

const addTransformationButton =
    document.getElementById("addTransformationButton");

const transformationForm =
    document.getElementById("transformationForm");

const transformationType =
    document.getElementById("transformationType");

const transformationColumns =
    document.getElementById("transformationColumns");

const transformationColumnsHelp =
    document.getElementById("transformationColumnsHelp");

const transformationOutput =
    document.getElementById("transformationOutput");

const cancelTransformationButton =
    document.getElementById("cancelTransformationButton");

const saveTransformationButton =
    document.getElementById("saveTransformationButton");

const transformationsList =
    document.getElementById("transformationsList");


// =====================================================
// ESTADO GENERAL
// =====================================================

let selectedFile = null;

let uploadedFilename = null;

let excelAnalysis = null;

let selectedColumns = [];

// =====================================================
// SELECCIÓN DE COLUMNAS POR HOJA
// =====================================================
//
// Ejemplo:
//
// {
//     "Hoja 1": ["Nombre", "Importe"],
//     "Hoja 2": ["Nombre", "DNI", "Importe"]
// }
//
// =====================================================

let selectedColumnsBySheet = {};

let transformations = [];

// =====================================================
// TRANSFORMACIONES POR HOJA
// =====================================================
//
// Ejemplo:
//
// {
//     "Hoja 1": [
//         {
//             operation: "sum",
//             columns: ["A", "B"],
//             output: "Total"
//         }
//     ],
//     "Hoja 2": []
// }
//
// =====================================================

let transformationsBySheet = {};


// =====================================================
// ESTADO DE COLUMNAS ELIMINADAS
// =====================================================
//
// Ejemplo:
//
// {
//     "Hoja 1": ["DNI"],
//     "Hoja 2": ["Direccion"]
// }
//
// =====================================================

let removedColumnsBySheet = {};


// =====================================================
// ESTADO DEL VISOR
// =====================================================

const PREVIEW_PAGE_SIZE = 25;

let currentSheetIndex = 0;

let currentPage = 1;

let currentPreviewRows = [];

let currentTotalPages = 1;

let selectedRows = {};


// =====================================================
// CLIENTES
// =====================================================

async function loadClients() {

    try {

        const response =
            await fetch("/api/clients");

        if (!response.ok) {

            throw new Error(
                "No se pudieron cargar los clientes."
            );
        }

        const data =
            await response.json();

        const clients =
            Array.isArray(data)
                ? data
                : (data.clients || []);

        clientSelect.innerHTML = `
            <option value="">
                Selecciona un cliente
            </option>
        `;

        for (
            const client
            of clients
        ) {

            const option =
                document.createElement("option");

            option.value =
                client.id;

            option.textContent =
                client.name;

            clientSelect.appendChild(option);
        }

    } catch (error) {

        console.error(error);

        clientSelect.innerHTML = `
            <option value="">
                Error al cargar clientes
            </option>
        `;
    }
}


// =====================================================
// CLIENTE
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

        await loadConversions(clientId);
    }
);


// =====================================================
// CONVERSION
// =====================================================

conversionSelect.addEventListener(
    "change",
    () => {

        updateButton();
    }
);


// =====================================================
// RESET CONVERSION
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

    transformationsBySheet = {};

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
                document.createElement("option");

            option.value =
                conversion.id;

            option.textContent =
                conversion.name;

            conversionSelect.appendChild(option);
        }

        conversionSelect.disabled =
            data.conversions.length === 0;

    } catch (error) {

        console.error(error);

        conversionSelect.innerHTML = `
            <option value="">
                Error al cargar conversiones
            </option>
        `;
    }

    updateButton();
}


// =====================================================
// SELECCIONAR ARCHIVO
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
    event => {

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
    event => {

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

async function handleFile(
    file
) {

    const extension =
        file.name
            .substring(
                file.name.lastIndexOf(".")
            )
            .toLowerCase();

    if (
        extension !== ".xlsx" &&
        extension !== ".xls"
    ) {

        showStatus(
            "El archivo debe ser un Excel .xlsx o .xls.",
            "error"
        );

        return;
    }

    selectedFile = file;

    uploadedFilename = null;

    excelAnalysis = null;

    selectedColumns = [];

    selectedColumnsBySheet = {};

    transformations = [];

    transformationsBySheet = {};

    removedColumnsBySheet = {};

    resetViewer();

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

async function uploadFile(
    file
) {

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

        console.error(error);

        showStatus(
            `Error: ${error.message}`,
            "error"
        );

        updateButton();
    }
}


// =====================================================
// ANALIZAR
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

        showAnalysis(data);

        updateButton();

    } catch (error) {

        console.error(error);

        showStatus(
            `Error al analizar el Excel: ${error.message}`,
            "error"
        );

        updateButton();
    }
}


// =====================================================
// MOSTRAR ANÁLISIS
// =====================================================

function showAnalysis(
    data
) {

    const sheets =
        data.sheets || [];

    if (
        sheets.length === 0
    ) {

        showStatus(
            "El Excel no contiene ninguna hoja.",
            "error"
        );

        return;
    }

    const totalRows =
        sheets.reduce(
            (
                total,
                sheet
            ) =>
                total + sheet.rows,
            0
        );

    const totalColumns =
        sheets.reduce(
            (
                total,
                sheet
            ) =>
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

    currentSheetIndex = 0;

    currentPage = 1;

    currentPreviewRows = [];

    currentTotalPages = 1;

    selectedRows = {};

    removedColumnsBySheet = {};

    selectedColumnsBySheet = {};

    transformationsBySheet = {};

    // ---------------------------------------------
    // Inicializar el estado de cada hoja
    // ---------------------------------------------

    for (
        const sheet
        of sheets
    ) {

        const sheetColumns =
            (
                sheet.column_details || []
            )
                .map(
                    column =>
                        typeof column === "string"
                            ? column
                            : column.name
                )
                .filter(
                    name =>
                        name &&
                        !name.startsWith(
                            "Unnamed:"
                        )
                );

        selectedColumnsBySheet[
            sheet.name
        ] = [
            ...sheetColumns
        ];

        transformationsBySheet[
            sheet.name
        ] = [];
    }

    const firstSheet =
        sheets[0];

    const firstSheetColumns =
        firstSheet
            ? (
                firstSheet.column_details || []
            )
                .map(
                    column =>
                        typeof column === "string"
                            ? column
                            : column.name
                )
                .filter(
                    name =>
                        name &&
                        !name.startsWith(
                            "Unnamed:"
                        )
                )
            : [];

    selectedColumns =
        [
            ...(selectedColumnsBySheet[
                firstSheet?.name
            ] || firstSheetColumns)
        ];

    transformations = [];

    renderColumns(
        getCurrentSheetColumns()
    );

    updateColumnSelectionCount();

    renderViewerSheets();

    renderViewer();

    renderTransformations();

    showStatus(
        "",
        ""
    );
}


// =====================================================
// ESTADO DE LA HOJA ACTUAL
// =====================================================

function getCurrentSheetName() {

    const sheet =
        getCurrentSheet();

    return sheet
        ? sheet.name
        : null;
}


function syncCurrentSheetState() {

    const sheetName =
        getCurrentSheetName();

    if (!sheetName) {

        return;
    }

    selectedColumnsBySheet[
        sheetName
    ] = [
        ...selectedColumns
    ];

    transformationsBySheet[
        sheetName
    ] = [
        ...transformations
    ];
}


function loadCurrentSheetState() {

    const sheetName =
        getCurrentSheetName();

    if (!sheetName) {

        selectedColumns = [];

        transformations = [];

        return;
    }

    const availableColumns =
        getAvailableColumns();

    const storedColumns =
        selectedColumnsBySheet[
            sheetName
        ];

    selectedColumns =
        (
            storedColumns ||
            availableColumns
        )
            .filter(
                column =>
                    availableColumns.includes(
                        column
                    )
            );

    if (
        selectedColumns.length === 0 &&
        availableColumns.length > 0
    ) {

        selectedColumns =
            [
                ...availableColumns
            ];
    }

    transformations =
        [
            ...(transformationsBySheet[
                sheetName
            ] || [])
        ];
}


// =====================================================
// COLUMNAS
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

    const availableColumns =
        getAvailableColumns();

    const filteredColumns =
        availableColumns.filter(
            name =>
                name
                    .toLowerCase()
                    .includes(searchTerm)
        );

    for (
        const name
        of filteredColumns
    ) {

        const label =
            document.createElement("label");

        label.className =
            "column-option";

        const checkbox =
            document.createElement("input");

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

                const currentSheetName =
                    getCurrentSheetName();

                if (
                    currentSheetName
                ) {

                    selectedColumnsBySheet[
                        currentSheetName
                    ] = [
                        ...selectedColumns
                    ];
                }

                updateColumnSelectionCount();

                renderViewer();

                renderTransformationColumns();

                updateButton();
            }
        );

        const text =
            document.createElement("span");

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
// ELIMINAR COLUMNAS NO SELECCIONADAS
// =====================================================

if (
    removeUnselectedColumnsButton
) {

    removeUnselectedColumnsButton.addEventListener(
        "click",
        () => {

            if (!excelAnalysis) {

                return;
            }

            const sheet =
                getCurrentSheet();

            if (!sheet) {

                return;
            }

            const availableColumns =
                getAvailableColumns();

            if (
                availableColumns.length === 0
            ) {

                return;
            }

            if (
                selectedColumns.length === 0
            ) {

                showStatus(
                    "Selecciona al menos una columna que quieras conservar.",
                    "error"
                );

                return;
            }

            const columnsToRemove =
                availableColumns.filter(
                    column =>
                        !selectedColumns.includes(
                            column
                        )
                );

            if (
                columnsToRemove.length === 0
            ) {

                showStatus(
                    "No hay columnas para eliminar.",
                    "error"
                );

                return;
            }

            const sheetName =
                sheet.name;

            if (
                !removedColumnsBySheet[
                    sheetName
                ]
            ) {

                removedColumnsBySheet[
                    sheetName
                ] = [];
            }

            for (
                const column
                of columnsToRemove
            ) {

                if (
                    !removedColumnsBySheet[
                        sheetName
                    ].includes(
                        column
                    )
                ) {

                    removedColumnsBySheet[
                        sheetName
                    ].push(
                        column
                    );
                }
            }

            selectedColumns =
                selectedColumns.filter(
                    column =>
                        !columnsToRemove.includes(
                            column
                        )
                );

            selectedColumnsBySheet[
                sheetName
            ] = [
                ...selectedColumns
            ];

            renderColumns(
                getCurrentSheetColumns()
            );

            updateColumnSelectionCount();

            renderViewer();

            renderTransformationColumns();

            updateButton();

            showStatus(
                `${columnsToRemove.length} columna(s) eliminada(s) del visor.`,
                "success"
            );
        }
    );
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

        renderColumns(
            getCurrentSheetColumns()
        );
    }
);


// =====================================================
// TODAS LAS COLUMNAS
// =====================================================

selectAllColumnsButton.addEventListener(
    "click",
    () => {

        selectedColumns =
            getAvailableColumns();

        const sheetName =
            getCurrentSheetName();

        if (sheetName) {

            selectedColumnsBySheet[
                sheetName
            ] = [
                ...selectedColumns
            ];
        }

        renderColumns(
            getCurrentSheetColumns()
        );

        updateColumnSelectionCount();

        renderViewer();

        renderTransformationColumns();

        updateButton();
    }
);


// =====================================================
// NINGUNA COLUMNA
// =====================================================

deselectAllColumnsButton.addEventListener(
    "click",
    () => {

        selectedColumns = [];

        const sheetName =
            getCurrentSheetName();

        if (sheetName) {

            selectedColumnsBySheet[
                sheetName
            ] = [];
        }

        renderColumns(
            getCurrentSheetColumns()
        );

        updateColumnSelectionCount();

        renderViewer();

        renderTransformationColumns();

        updateButton();
    }
);


// =====================================================
// CONTADOR COLUMNAS
// =====================================================

function updateColumnSelectionCount() {

    const total =
        getAvailableColumns().length;

    columnSelectionCount.textContent =
        `${selectedColumns.length} de ${total} columnas seleccionadas`;
}


// =====================================================
// COLUMNAS DISPONIBLES
// =====================================================

function getAvailableColumns() {

    const sheet =
        getCurrentSheet();

    if (!sheet) {

        return [];
    }

    const sheetName =
        sheet.name;

    const removedColumns =
        removedColumnsBySheet[
            sheetName
        ] || [];

    return (
        sheet.column_details || []
    )
        .map(
            column =>
                String(column.name)
        )
        .filter(
            name =>
                name &&
                !name.startsWith(
                    "Unnamed:"
                ) &&
                !removedColumns.includes(
                    name
                )
        );
}


// =====================================================
// HOJAS
// =====================================================

function renderViewerSheets() {

    viewerSheet.innerHTML =
        "";

    if (!excelAnalysis) {

        return;
    }

    const sheets =
        excelAnalysis.sheets || [];

    sheets.forEach(
        (
            sheet,
            index
        ) => {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                String(index);

            option.textContent =
                sheet.name;

            viewerSheet.appendChild(
                option
            );
        }
    );

    viewerSheet.value =
        String(currentSheetIndex);
}


// =====================================================
// CAMBIO DE HOJA
// =====================================================

viewerSheet.addEventListener(
    "change",
    async () => {

        // Guardamos el estado de la hoja anterior
        syncCurrentSheetState();

        currentSheetIndex =
            Number(
                viewerSheet.value
            );

        currentPage = 1;

        currentPreviewRows = [];

        currentTotalPages = 1;

        // Cargamos el estado de la nueva hoja
        loadCurrentSheetState();

        renderColumns(
            getCurrentSheetColumns()
        );

        updateColumnSelectionCount();

        renderTransformationColumns();

        renderTransformations();

        await loadPreviewPage();
    }
);


// =====================================================
// HOJA ACTUAL
// =====================================================

function getCurrentSheet() {

    if (!excelAnalysis) {

        return null;
    }

    return (
        excelAnalysis.sheets[
            currentSheetIndex
        ] || null
    );
}


// =====================================================
// COLUMNAS HOJA ACTUAL
// =====================================================

function getCurrentSheetColumns() {

    const sheet =
        getCurrentSheet();

    if (!sheet) {

        return [];
    }

    return (
        sheet.column_details || []
    );
}


// =====================================================
// CARGAR PÁGINA DESDE BACKEND
// =====================================================

async function loadPreviewPage() {

    if (
        !uploadedFilename ||
        !excelAnalysis
    ) {

        return;
    }

    const sheet =
        getCurrentSheet();

    if (!sheet) {

        return;
    }

    showStatus(
        "Cargando filas...",
        "loading"
    );

    try {

        const url =
            `/api/preview/` +
            `${encodeURIComponent(
                uploadedFilename
            )}` +
            `?sheet=${encodeURIComponent(
                sheet.name
            )}` +
            `&page=${currentPage}` +
            `&page_size=${PREVIEW_PAGE_SIZE}`;

        const response =
            await fetch(url);

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "No se pudo cargar la página."
            );
        }

        currentPreviewRows =
            data.rows || [];

        currentPage =
            data.page || currentPage;

        currentTotalPages =
            data.total_pages || 1;

        renderViewerTable(sheet);

        updateViewerPagination(data);

        updateRowSelectionCount();

        updatePaginationButtons();

        showStatus(
            "",
            ""
        );

    } catch (error) {

        console.error(error);

        showStatus(
            `Error al cargar las filas: ${error.message}`,
            "error"
        );
    }
}


// =====================================================
// RENDER VISOR
// =====================================================

function renderViewer() {

    const sheet =
        getCurrentSheet();

    if (!sheet) {

        excelViewer.classList.add(
            "hidden"
        );

        return;
    }

    excelViewer.classList.remove(
        "hidden"
    );

    if (
        currentPreviewRows.length === 0 &&
        currentPage === 1 &&
        sheet.preview
    ) {

        currentPreviewRows =
            sheet.preview;

        currentTotalPages =
            Math.max(
                1,
                Math.ceil(
                    sheet.rows /
                    PREVIEW_PAGE_SIZE
                )
            );
    }

    renderViewerTable(sheet);

    updateViewerPagination();

    updateRowSelectionCount();

    updatePaginationButtons();
}


// =====================================================
// TABLA
// =====================================================

function renderViewerTable(
    sheet
) {

    excelTableHead.innerHTML =
        "";

    excelTableBody.innerHTML =
        "";

    const visibleRows =
        currentPreviewRows || [];

    const availableColumns =
        getAvailableColumns();


    // =================================================
    // CABECERA
    // =================================================

    const headerRow =
        document.createElement("tr");


    const selectHeader =
        document.createElement("th");

    selectHeader.className =
        "row-checkbox-cell";


    const selectCheckbox =
        document.createElement("input");

    selectCheckbox.type =
        "checkbox";

    selectCheckbox.checked =
        areAllCurrentPageRowsSelected(
            visibleRows
        );


    selectCheckbox.addEventListener(
        "change",
        () => {

            if (
                selectCheckbox.checked
            ) {

                selectCurrentPageRows(
                    visibleRows
                );

            } else {

                deselectCurrentPageRows(
                    visibleRows
                );
            }

            renderViewer();

            updateRowSelectionCount();
        }
    );


    selectHeader.appendChild(
        selectCheckbox
    );

    headerRow.appendChild(
        selectHeader
    );


    // =================================================
    // NÚMERO DE FILA
    // =================================================

    const numberHeader =
        document.createElement("th");

    numberHeader.className =
        "row-number";

    numberHeader.textContent =
        "#";

    headerRow.appendChild(
        numberHeader
    );


    // =================================================
    // COLUMNAS
    // =================================================

    for (
        const column
        of availableColumns
    ) {

        const th =
            document.createElement("th");

        th.className =
            "column-header";


        const content =
            document.createElement("div");

        content.className =
            "column-header-content";


        const checkbox =
            document.createElement("input");

        checkbox.type =
            "checkbox";

        checkbox.checked =
            selectedColumns.includes(
                column
            );


        checkbox.addEventListener(
            "click",
            event => {

                event.stopPropagation();
            }
        );


        checkbox.addEventListener(
            "change",
            () => {

                if (
                    checkbox.checked
                ) {

                    if (
                        !selectedColumns.includes(
                            column
                        )
                    ) {

                        selectedColumns.push(
                            column
                        );
                    }

                } else {

                    selectedColumns =
                        selectedColumns.filter(
                            item =>
                                item !==
                                column
                        );
                }

                const sheetName =
                    getCurrentSheetName();

                if (sheetName) {

                    selectedColumnsBySheet[
                        sheetName
                    ] = [
                        ...selectedColumns
                    ];
                }

                renderColumns(
                    getCurrentSheetColumns()
                );

                updateColumnSelectionCount();

                renderViewer();

                renderTransformationColumns();

                updateButton();
            }
        );


        const text =
            document.createElement("span");

        text.textContent =
            column;


        content.appendChild(
            checkbox
        );

        content.appendChild(
            text
        );


        th.appendChild(
            content
        );

        headerRow.appendChild(
            th
        );
    }


    excelTableHead.appendChild(
        headerRow
    );


    // =================================================
    // FILAS
    // =================================================

    for (
        const row
        of visibleRows
    ) {

        const tr =
            document.createElement("tr");

        const rowNumber =
            row._row_number;


        if (
            isRowSelected(
                rowNumber
            )
        ) {

            tr.classList.add(
                "selected"
            );
        }


        // ---------------------------------------------
        // CHECKBOX FILA
        // ---------------------------------------------

        const checkboxCell =
            document.createElement("td");

        checkboxCell.className =
            "row-checkbox-cell";


        const rowCheckbox =
            document.createElement("input");

        rowCheckbox.type =
            "checkbox";

        rowCheckbox.checked =
            isRowSelected(
                rowNumber
            );


        rowCheckbox.addEventListener(
            "change",
            () => {

                if (
                    rowCheckbox.checked
                ) {

                    selectRow(
                        rowNumber
                    );

                } else {

                    deselectRow(
                        rowNumber
                    );
                }

                renderViewer();

                updateRowSelectionCount();
            }
        );


        checkboxCell.appendChild(
            rowCheckbox
        );

        tr.appendChild(
            checkboxCell
        );


        // ---------------------------------------------
        // NÚMERO
        // ---------------------------------------------

        const numberCell =
            document.createElement("td");

        numberCell.className =
            "row-number";

        numberCell.textContent =
            rowNumber;

        tr.appendChild(
            numberCell
        );


        // ---------------------------------------------
        // DATOS
        // ---------------------------------------------

        for (
            const column
            of availableColumns
        ) {

            const td =
                document.createElement("td");

            let value =
                row[column];


            if (
                value === null ||
                value === undefined
            ) {

                value = "";
            }


            td.textContent =
                String(value);

            td.title =
                String(value);

            tr.appendChild(
                td
            );
        }


        excelTableBody.appendChild(
            tr
        );
    }
}
// =====================================================
// SELECCIÓN FILAS
// =====================================================

function getRowKey(
    rowNumber
) {

    const sheet =
        getCurrentSheet();

    const sheetName =
        sheet
            ? sheet.name
            : currentSheetIndex;

    return (
        `${sheetName}::${rowNumber}`
    );
}


function isRowSelected(
    rowNumber
) {

    return Boolean(
        selectedRows[
            getRowKey(
                rowNumber
            )
        ]
    );
}


function selectRow(
    rowNumber
) {

    selectedRows[
        getRowKey(
            rowNumber
        )
    ] = true;
}


function deselectRow(
    rowNumber
) {

    delete selectedRows[
        getRowKey(
            rowNumber
        )
    ];
}


// =====================================================
// SELECCIONAR PÁGINA
// =====================================================

function selectCurrentPageRows(
    rows
) {

    for (
        const row
        of rows
    ) {

        selectRow(
            row._row_number
        );
    }
}


function deselectCurrentPageRows(
    rows
) {

    for (
        const row
        of rows
    ) {

        deselectRow(
            row._row_number
        );
    }
}


function areAllCurrentPageRowsSelected(
    rows
) {

    if (
        rows.length === 0
    ) {

        return false;
    }

    return rows.every(
        row =>
            isRowSelected(
                row._row_number
            )
    );
}


// =====================================================
// BOTONES FILAS
// =====================================================

selectAllRowsButton.addEventListener(
    "click",
    () => {

        selectCurrentPageRows(
            currentPreviewRows
        );

        renderViewer();

        updateRowSelectionCount();
    }
);


deselectAllRowsButton.addEventListener(
    "click",
    () => {

        deselectCurrentPageRows(
            currentPreviewRows
        );

        renderViewer();

        updateRowSelectionCount();
    }
);


// =====================================================
// CONTADOR FILAS
// =====================================================

function getSelectedRowsCount() {

    return Object.keys(
        selectedRows
    ).length;
}


function updateRowSelectionCount() {

    rowSelectionCount.textContent =
        `${getSelectedRowsCount()} fila(s) seleccionada(s)`;
}


// =====================================================
// PAGINACIÓN
// =====================================================

previousPageButton.addEventListener(
    "click",
    async () => {

        if (
            currentPage <= 1
        ) {

            return;
        }

        currentPage--;

        await loadPreviewPage();
    }
);


nextPageButton.addEventListener(
    "click",
    async () => {

        if (
            currentPage >=
            currentTotalPages
        ) {

            return;
        }

        currentPage++;

        await loadPreviewPage();
    }
);


// =====================================================
// INFORMACIÓN PAGINACIÓN
// =====================================================

function updateViewerPagination(
    data = null
) {

    const totalRows =
        data
            ? data.total_rows
            : (
                getCurrentSheet()
                    ?.rows || 0
            );


    const totalPages =
        data
            ? data.total_pages
            : currentTotalPages;


    const startRow =
        data?.start_row || null;

    const endRow =
        data?.end_row || null;


    if (
        startRow !== null &&
        endRow !== null
    ) {

        viewerPagination.textContent =
            `Mostrando ${startRow}–${endRow} ` +
            `de ${totalRows} filas`;

    } else {

        viewerPagination.textContent =
            `Página ${currentPage} ` +
            `de ${totalPages} · ` +
            `${totalRows} filas`;
    }


    viewerDetails.textContent =
        `Vista previa de la hoja ` +
        `"${getCurrentSheet()?.name || ""}".`;
}


// =====================================================
// BOTONES PAGINACIÓN
// =====================================================

function updatePaginationButtons() {

    previousPageButton.disabled =
        currentPage <= 1;

    nextPageButton.disabled =
        currentPage >=
        currentTotalPages;

    currentPageElement.textContent =
        currentPage;
}


// =====================================================
// RESET VISOR
// =====================================================

function resetViewer() {

    currentSheetIndex = 0;

    currentPage = 1;

    currentPreviewRows = [];

    currentTotalPages = 1;

    selectedRows = {};

    removedColumnsBySheet = {};

    excelViewer.classList.add(
        "hidden"
    );

    excelTableHead.innerHTML =
        "";

    excelTableBody.innerHTML =
        "";

    viewerSheet.innerHTML =
        "";

    viewerPagination.textContent =
        "Página 1 de 1";

    rowSelectionCount.textContent =
        "0 filas seleccionadas";

    currentPageElement.textContent =
        "1";

    previousPageButton.disabled =
        true;

    nextPageButton.disabled =
        true;
}


// =====================================================
// FILAS SELECCIONADAS POR HOJA
// =====================================================

function getSelectedRowsBySheet() {

    const result = {};

    for (
        const key
        of Object.keys(
            selectedRows
        )
    ) {

        const separatorIndex =
            key.lastIndexOf("::");

        if (
            separatorIndex === -1
        ) {

            continue;
        }

        const sheetName =
            key.substring(
                0,
                separatorIndex
            );

        const rowNumber =
            Number(
                key.substring(
                    separatorIndex + 2
                )
            );

        if (
            !Number.isInteger(
                rowNumber
            )
        ) {

            continue;
        }

        if (
            !result[sheetName]
        ) {

            result[sheetName] = [];
        }

        result[sheetName].push(
            rowNumber
        );
    }


    for (
        const sheetName
        of Object.keys(
            result
        )
    ) {

        result[sheetName].sort(
            (
                a,
                b
            ) =>
                a - b
        );
    }


    return result;
}


// =====================================================
// TRANSFORMACIONES
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
            document.createElement("div");

        card.className =
            "transformation-card";

        const header =
            document.createElement("div");

        header.className =
            "transformation-card-header";

        const title =
            document.createElement("div");

        title.className =
            "transformation-card-title";

        title.textContent =
            transformation.output;

        const removeButton =
            document.createElement("button");

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

                const sheetName =
                    getCurrentSheetName();

                if (sheetName) {

                    transformationsBySheet[
                        sheetName
                    ] = [
                        ...transformations
                    ];
                }

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
            document.createElement("div");

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
// LABEL OPERACIÓN
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
// TIPO TRANSFORMACIÓN
// =====================================================

transformationType.addEventListener(
    "change",
    () => {

        renderTransformationColumns();
    }
);


// =====================================================
// COLUMNAS TRANSFORMACIÓN
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
            document.createElement("label");

        label.className =
            "transformation-column-option";

        const checkbox =
            document.createElement("input");

        checkbox.type =
            "checkbox";

        checkbox.value =
            column.name;

        const text =
            document.createElement("span");

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
        "Solo se muestran columnas numéricas compatibles con esta operación.";
}


// =====================================================
// COLUMNAS NUMÉRICAS
// =====================================================

function getNumericColumns() {

    const sheet =
        getCurrentSheet();

    if (!sheet) {

        return [];
    }

    const availableColumns =
        new Set(
            getAvailableColumns()
        );

    return (
        sheet.column_details || []
    ).filter(
        column => {

            const name =
                String(
                    column.name || ""
                );

            if (
                !availableColumns.has(
                    name
                )
            ) {

                return false;
            }

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
            ).map(
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
                "Selecciona al menos dos columnas.",
                "error"
            );

            return;
        }

        if (!output) {

            showStatus(
                "Escribe el nombre de la nueva columna.",
                "error"
            );

            return;
        }

        if (
            getAvailableColumns()
                .includes(
                    output
                )
        ) {

            showStatus(
                "El nombre de la nueva columna ya existe.",
                "error"
            );

            return;
        }

        const transformation = {

            operation:
                operation,

            columns:
                columns,

            output:
                output
        };

        transformations.push(
            transformation
        );

        const sheetName =
            getCurrentSheetName();

        if (sheetName) {

            transformationsBySheet[
                sheetName
            ] = [
                ...transformations
            ];
        }

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
// RESET TRANSFORMACIÓN
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
        Object.values(
            selectedColumnsBySheet
        )
            .some(
                columns =>
                    Array.isArray(columns) &&
                    columns.length > 0
            );

    convertButton.disabled = !(
        clientSelected &&
        conversionSelected &&
        fileSelected &&
        fileAnalyzed &&
        columnsSelected
    );
}


// =====================================================
// PREPARAR ESTADO POR HOJA
// =====================================================

function prepareSheetState() {

    syncCurrentSheetState();

    const selectedColumns =
        {};

    const transformations =
        {};

    const removedColumns =
        {};

    for (
        const sheet
        of excelAnalysis.sheets
    ) {

        const sheetName =
            sheet.name;

        selectedColumns[
            sheetName
        ] = [
            ...(
                selectedColumnsBySheet[
                    sheetName
                ] || []
            )
        ];

        transformations[
            sheetName
        ] = [
            ...(
                transformationsBySheet[
                    sheetName
                ] || []
            )
        ];

        removedColumns[
            sheetName
        ] = [
            ...(
                removedColumnsBySheet[
                    sheetName
                ] || []
            )
        ];
    }

    return {
        selectedColumns,
        transformations,
        removedColumns
    };
}


// =====================================================
// CONVERTIR
// =====================================================

convertButton.addEventListener(
    "click",
    async () => {

        syncCurrentSheetState();

        if (
            !selectedFile ||
            !clientSelect.value ||
            !conversionSelect.value ||
            !excelAnalysis
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

            // =========================================
            // SUBIR
            // =========================================

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


            // =========================================
            // ESTADO POR HOJA
            // =========================================

            const sheetState =
                prepareSheetState();


            // =========================================
            // PARÁMETROS
            // =========================================

            const clientId =
                clientSelect.value;

            const conversionId =
                conversionSelect.value;

            const selectedColumnsParam =
                encodeURIComponent(
                    JSON.stringify(
                        sheetState.selectedColumns
                    )
                );

            const transformationsParam =
                encodeURIComponent(
                    JSON.stringify(
                        sheetState.transformations
                    )
                );

            const removedColumnsParam =
                encodeURIComponent(
                    JSON.stringify(
                        sheetState.removedColumns
                    )
                );

            const selectedRowsParam =
                encodeURIComponent(
                    JSON.stringify(
                        getSelectedRowsBySheet()
                    )
                );


            // =========================================
            // URL
            // =========================================

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
                `&transformations=${transformationsParam}` +
                `&removed_columns=${removedColumnsParam}` +
                `&selected_rows=${selectedRowsParam}`;


            // =========================================
            // CONVERTIR
            // =========================================

            showStatus(
                "Convirtiendo archivo...",
                "loading"
            );

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


            // =========================================
            // DESCARGAR
            // =========================================

            const blob =
                await convertResponse.blob();

            const downloadUrl =
                window.URL.createObjectURL(
                    blob
                );

            const link =
                document.createElement("a");

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
// STATUS
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