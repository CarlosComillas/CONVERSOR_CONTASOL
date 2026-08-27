const fileInput = document.getElementById("fileInput");
const selectFileButton = document.getElementById("selectFile");
const uploadArea = document.getElementById("uploadArea");
const fileName = document.getElementById("fileName");
const convertButton = document.getElementById("convertButton");
const clientSelect = document.getElementById("client");
const status = document.getElementById("status");

let selectedFile = null;

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


clientSelect.addEventListener("change", updateButton);


function handleFile(file) {

    const validExtensions = [".xlsx", ".xls"];

    const extension = file.name
        .substring(file.name.lastIndexOf("."))
        .toLowerCase();

    if (!validExtensions.includes(extension)) {
        showStatus(
            "El archivo debe ser un Excel (.xlsx o .xls).",
            "error"
        );

        return;
    }

    selectedFile = file;

    fileName.textContent = `Archivo seleccionado: ${file.name}`;

    showStatus("", "");

    updateButton();
}


function updateButton() {

    const clientSelected = clientSelect.value !== "";
    const fileSelected = selectedFile !== null;

    convertButton.disabled = !(clientSelected && fileSelected);
}


function showStatus(message, type) {

    if (!message) {
        status.classList.add("hidden");
        status.textContent = "";
        return;
    }

    status.classList.remove("hidden");
    status.textContent = message;
}

loadClients();