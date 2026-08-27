const fileInput = document.getElementById("fileInput");
const selectFileButton = document.getElementById("selectFile");
const uploadArea = document.getElementById("uploadArea");
const fileName = document.getElementById("fileName");
const convertButton = document.getElementById("convertButton");
const clientSelect = document.getElementById("client");
const conversionSelect = document.getElementById("conversion");
const status = document.getElementById("status");
const fileAnalysis = document.getElementById("fileAnalysis");
const fileAnalysisStatus = document.getElementById("fileAnalysisStatus");
const fileAnalysisDetails = document.getElementById("fileAnalysisDetails");

let selectedFile = null;
let uploadedFilename = null;
let excelAnalysis = null;


// ==============================
// CLIENTES
// ==============================

async function loadClients() {
    try {
        const response = await fetch("/api/clients");

        if (!response.ok) {
            throw new Error("No se pudieron cargar los clientes.");
        }

        const data = await response.json();

        clientSelect.innerHTML = `
            <option value="">Selecciona un cliente</option>
        `;

        for (const client of data.clients) {
            const option = document.createElement("option");

            option.value = client.id;
            option.textContent = client.name;

            clientSelect.appendChild(option);
        }

    } catch (error) {
        clientSelect.innerHTML = `
            <option value="">Error al cargar clientes</option>
        `;

        console.error(error);
    }
}


// ==============================
// SELECCIÓN DE ARCHIVO
// ==============================

selectFileButton.addEventListener("click", () => {
    fileInput.click();
});


fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});


uploadArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadArea.classList.add("dragover");
});


uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
});


uploadArea.addEventListener("drop", (event) => {
    event.preventDefault();

    uploadArea.classList.remove("dragover");

    if (event.dataTransfer.files.length > 0) {
        handleFile(event.dataTransfer.files[0]);
    }
});


clientSelect.addEventListener("change", async () => {

    const clientId = clientSelect.value;

    if (!clientId) {

        conversionSelect.innerHTML = `
            <option value="">
                Selecciona primero un cliente
            </option>
        `;
        conversionSelect.disabled = true;

        updateButton();

        return;
    }

    await loadConversions(clientId);
});

conversionSelect.addEventListener(
    "change",
    updateButton
);


// ==============================
// MANEJO DEL ARCHIVO
// ==============================

async function handleFile(file) {

    const validExtensions = [".xlsx"];

    const extension = file.name
        .substring(file.name.lastIndexOf("."))
        .toLowerCase();

    if (!validExtensions.includes(extension)) {
        showStatus(
            "El archivo debe ser un Excel .xlsx.",
            "error"
        );

        return;
    }

    selectedFile = file;
    uploadedFilename = null;
    excelAnalysis = null;

    fileName.textContent = `Archivo seleccionado: ${file.name}`;

    updateButton();

    await uploadFile(file);
}


// ==============================
// SUBIR EXCEL AL BACKEND
// ==============================

async function uploadFile(file) {

    showStatus("Subiendo archivo...", "loading");

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "No se pudo subir el archivo."
            );
        }

        uploadedFilename = data.filename;

        showStatus("Excel subido. Analizando archivo...", "loading");

        await analyzeFile(uploadedFilename);

    } catch (error) {

        uploadedFilename = null;
        excelAnalysis = null;

        showStatus(
            `Error: ${error.message}`,
            "error"
        );

        console.error(error);

        updateButton();
    }
}


// ==============================
// ANALIZAR EXCEL
// ==============================

async function analyzeFile(filename) {

    try {

        const response = await fetch(
            `/api/analyze/${encodeURIComponent(filename)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "No se pudo analizar el Excel."
            );
        }

        excelAnalysis = data;

        showAnalysis(data);

        updateButton();

    } catch (error) {

        excelAnalysis = null;

        showStatus(
            `Error al analizar el Excel: ${error.message}`,
            "error"
        );

        console.error(error);

        updateButton();
    }
}


// ==============================
// MOSTRAR INFORMACIÓN DEL EXCEL
// ==============================

function showAnalysis(data) {

    const sheets = data.sheets || [];

    if (sheets.length === 0) {
        showStatus(
            "El Excel no contiene ninguna hoja.",
            "error"
        );

        fileAnalysis.classList.add("hidden");

        return;
    }

    const totalRows = sheets.reduce(
        (total, sheet) => total + sheet.rows,
        0
    );

    const totalColumns = sheets.reduce(
        (total, sheet) => total + sheet.columns,
        0
    );

    fileAnalysis.classList.remove("hidden");

    fileAnalysisStatus.textContent =
        "✓ Excel analizado correctamente";

    fileAnalysisDetails.textContent =
        `${sheets.length} hoja(s) · ${totalRows} filas · ${totalColumns} columna(s)`;

    showStatus("", "");

    console.log("Análisis del Excel:", data);
}


// ==============================
// BOTÓN CONVERTIR
// ==============================

function updateButton() {

    const clientSelected =
        clientSelect.value !== "";

    const conversionSelected =
        conversionSelect.value !== "";

    const fileSelected =
        selectedFile !== null;

    const fileAnalyzed =
        excelAnalysis !== null;

    convertButton.disabled = !(
        clientSelected &&
        conversionSelected &&
        fileSelected &&
        fileAnalyzed
    );
}


// ==============================
// MENSAJES DE ESTADO
// ==============================

function showStatus(message, type) {

    if (!message) {
        status.classList.add("hidden");
        status.textContent = "";
        return;
    }

    status.classList.remove("hidden");
    status.textContent = message;

    status.className = "status";

    if (type) {
        status.classList.add(type);
    }
}

convertButton.addEventListener("click", async () => {
    if (!selectedFile || !clientSelect.value) {
        return;
    }

    convertButton.disabled = true;
    convertButton.textContent = "Convirtiendo...";

    showStatus("Preparando la conversión...", "info");

    try {
        // 1. Subir el archivo
        const formData = new FormData();
        formData.append("file", selectedFile);

        const uploadResponse = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        if (!uploadResponse.ok) {
            throw new Error("No se pudo subir el archivo.");
        }

        const uploadData = await uploadResponse.json();

        // 2. Convertir el archivo
        showStatus("Convirtiendo archivo...", "info");

        const clientId = clientSelect.value;
        const conversionId = conversionSelect.value;

        const convertResponse = await fetch(
            `/api/convert?filename=${encodeURIComponent(uploadData.filename)}` +
            `&client_id=${encodeURIComponent(clientId)}` +
            `&conversion_id=${encodeURIComponent(conversionId)}`,
            {
                method: "POST",
            }
        );

        if (!convertResponse.ok) {
            throw new Error("No se pudo convertir el archivo.");
        }

        // 3. Descargar el resultado
        const blob = await convertResponse.blob();

        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = `CONTASOL_${uploadData.filename}`;

        document.body.appendChild(link);
        link.click();
        link.remove();

        window.URL.revokeObjectURL(downloadUrl);

        showStatus(
            "✓ Conversión completada. El archivo se ha descargado.",
            "success"
        );

    } catch (error) {
        console.error(error);

        showStatus(
            "Ha ocurrido un error durante la conversión.",
            "error"
        );

    } finally {
        convertButton.disabled = false;
        convertButton.textContent = "Convertir a CONTASOL";
    }
});


// ==============================
// INICIO
// ==============================

loadClients();
async function loadConversions(clientId) {
    conversionSelect.innerHTML = `
        <option value="">Cargando conversiones...</option>
    `;

    conversionSelect.disabled = true;

    try {
        const response = await fetch(
            `/api/clients/${encodeURIComponent(clientId)}/conversions`
        );

        if (!response.ok) {
            throw new Error(
                "No se pudieron cargar las conversiones."
            );
        }

        const data = await response.json();

        conversionSelect.innerHTML = `
            <option value="">Selecciona una conversión</option>
        `;

        for (const conversion of data.conversions) {
            const option = document.createElement("option");

            option.value = conversion.id;
            option.textContent = conversion.name;

            conversionSelect.appendChild(option);
        }

        conversionSelect.disabled =
            data.conversions.length === 0;

        if (data.conversions.length === 0) {
            conversionSelect.innerHTML = `
                <option value="">
                    No hay conversiones configuradas
                </option>
            `;
        }

    } catch (error) {

        conversionSelect.innerHTML = `
            <option value="">
                Error al cargar conversiones
            </option>
        `;

        conversionSelect.disabled = true;

        console.error(error);
    }

    updateButton();
}