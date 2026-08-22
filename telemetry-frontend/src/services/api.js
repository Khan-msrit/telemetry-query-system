import axios from "axios";

const BASE_URL = "http://localhost:8000";

export async function fetchAutocomplete(q) {
  const res = await axios.get(`${BASE_URL}/autocomplete`, { params: { q } });
  return res.data;
}

export async function sendNlQuery(query) {
  const res = await axios.post(`${BASE_URL}/query`, { query });
  return res.data;
}