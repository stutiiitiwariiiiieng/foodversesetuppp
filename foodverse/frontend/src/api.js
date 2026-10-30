// In production set VITE_API_URL to the backend URL (no trailing slash). Empty = same origin / dev proxy.
const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function handle(res) {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try { const j = await res.json(); msg = j.detail || msg; } catch {}
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return res.json();
}

export const postFile = (url, file) => {
  const fd = new FormData();
  fd.append("file", file);
  return fetch(BASE + url, { method: "POST", body: fd }).then(handle);
};

export const postJson = (url, body) =>
  fetch(BASE + url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(handle);

export const getJson = (url) => fetch(BASE + url).then(handle);

export const postForm = (url, fields, file) => {
  const fd = new FormData();
  Object.entries(fields).forEach(([k, v]) => fd.append(k, v));
  if (file) fd.append("file", file);
  return fetch(BASE + url, { method: "POST", body: fd }).then(handle);
};
