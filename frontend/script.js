// Image Preview
document.getElementById("image").addEventListener("change", function() {
    const file = this.files[0];
    const preview = document.getElementById("preview");

    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.classList.remove("hidden");
    }
});

// Progress Bar Generator
function createProgressBar(label, value) {
    if (value === null || value === undefined) return "";

    let percent = Math.round(value * 100);

    return `
        <div class="progress-item">
            <p><strong>${label}:</strong> ${percent}%</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

// Form Submit
document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const loading = document.getElementById("loading");
    const resultContainer = document.getElementById("result");

    resultContainer.classList.add("hidden");
    loading.classList.remove("hidden");

    const formData = new FormData();
    const imageFile = document.getElementById("image").files[0];
    const textInput = document.getElementById("text").value;

    if (imageFile) formData.append("image", imageFile);
    if (textInput) formData.append("text", textInput);

    const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    loading.classList.add("hidden");
    resultContainer.classList.remove("hidden");

    // Risk color
    let riskClass = "";
    if (data.risk_level === "High") riskClass = "risk-high";
    else if (data.risk_level === "Medium") riskClass = "risk-medium";
    else riskClass = "risk-low";

    // Risk summary
    let summaryMessage = "";
    if (data.risk_level === "High") {
        summaryMessage = "⚠️ High risk content detected. Strong indicators of AI-generated manipulation.";
    } else if (data.risk_level === "Medium") {
        summaryMessage = "⚠️ Suspicious content detected. Review recommended.";
    } else {
        summaryMessage = "✅ Content appears safe based on AI analysis.";
    }

    resultContainer.innerHTML = `
        <div class="result-card ${riskClass}">
            <h3>Risk Level: ${data.risk_level}</h3>
            <p class="summary">${summaryMessage}</p>
            ${createProgressBar("Image Probability", data.image_probability)}
            ${createProgressBar("Text Probability", data.text_probability)}
            <p><strong>Explanation:</strong> ${data.explanation}</p>
        </div>
    `;
});
