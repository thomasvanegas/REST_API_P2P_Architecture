const API_URL = "http://127.0.0.1:8000/";

// Subir archivo.
document.getElementById("upload_form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file_input = document.getElementById("file_input");
    if (!file_input.files.length) return alert("Selecciona un archivo");

    const form_data = new FormData();
    form_data.append("file", file_input.files[0]);

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: form_data
    });

    const data = await response.json();
    alert(data.message);
    loadFiles();
});

// Listado de archivos.
async function loadFiles() {
    const response = await fetch(`${API_URL}/files`);
    const data = await response.json();
    const file_list = document.getElementById("file_list");
    file_list.innerHTML = "";
    data.files.forEach(file => {
        const li = document.createElement("li");
        li.innerHTML = `${file} <a href="${API_URL}/download/${file}" download>Descargar</a>`;
        file_list.appendChild(li);
    });
}

loadFiles();