const API = "http://localhost:8000";

export const getPlants = async () =>
  fetch(`${API}/plants`).then((r) => r.json());

export const getCurrentWeather = async (id) =>
  fetch(`${API}/weather/current/${id}`).then((r) => r.json());

export const getSolarRealtime = async (id) =>
  fetch(`${API}/solar/realtime/${id}`).then((r) => r.json());

export const getSolarForecast = async (id) =>
  fetch(`${API}/solar/forecast/${id}`).then((r) => r.json());

export const getDailyForecast = async (id) =>
  fetch(
    `${API}/forecast/daily/${id}?start_date=2025-01-01&end_date=2025-12-31`
  ).then((r) => r.json());
