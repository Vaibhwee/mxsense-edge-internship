import { fallbackBlueprint, fallbackOverview } from "./blueprint";


const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api/api-gateway";


async function fetchJson(path) {
  const response = await fetch(`${apiBase}${path}`, {
    next: { revalidate: 15 },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}


export async function getPlatformOverview() {
  try {
    return await fetchJson("/overview/");
  } catch (error) {
    return fallbackOverview;
  }
}


export async function getPlatformBlueprint() {
  return fallbackBlueprint;
}
