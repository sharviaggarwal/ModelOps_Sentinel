
const API_BASE_URL = "https://modelops-sentinel-api.onrender.com";

export async function getModelHealth() {
  const response = await fetch(`${API_BASE_URL}/monitor/health`);

  if (!response.ok) {
    throw new Error("Failed to fetch model health");
  }

  return response.json();
}

export async function getIncidents() {
  const response = await fetch(`${API_BASE_URL}/incidents`);

  if (!response.ok) {
    throw new Error("Failed to fetch incidents");
  }

  return response.json();
}

export async function triggerInvestigation(incidentId) {
  const url = `${API_BASE_URL}/agent/investigate/${incidentId}`;

  console.log("Sending investigation request:", url);

  const response = await fetch(url, {
    method: "POST",
  });

  console.log("Investigation HTTP status:", response.status);

  const data = await response.json();

  console.log("Investigation API response:", data);

  if (!response.ok) {
    throw new Error(data.detail || "Investigation failed");
  }

  return data;
}
export async function approveInvestigation(threadId, decision) {
  const url = `${API_BASE_URL}/agent/approve/${threadId}?decision=${decision}`;

  console.log("Sending approval request:", url);

  const response = await fetch(url, {
    method: "POST",
  });

  console.log("Approval HTTP status:", response.status);

  const data = await response.json();

  console.log("Approval API response:", data);

  if (!response.ok) {
    throw new Error(data.detail || "Approval failed");
  }

  return data;
}
