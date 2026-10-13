/**
 * API client for Satark backend service.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Sends text and/or screenshot image to POST /analyze
 * @param {Object} params
 * @param {string} [params.text] - Plain text message
 * @param {File} [params.image] - Screenshot file
 * @returns {Promise<Object>} AnalyzeResponse JSON
 */
export async function analyzeMessageOrScreenshot({ text, image }) {
  const formData = new FormData();

  if (text && text.trim()) {
    formData.append("text", text.trim());
  }

  if (image) {
    formData.append("image", image);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorDetail = "Server error occurred while analyzing message.";
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorDetail;
      } catch {
        // Fallback to HTTP status text
        errorDetail = `Error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorDetail);
    }

    const data = await response.json();
    return data;
  } catch (err) {
    if (err.name === "TypeError" && err.message.includes("fetch")) {
      throw new Error("Cannot connect to Satark analysis server. Please ensure the backend is running at " + API_BASE_URL);
    }
    throw err;
  }
}
