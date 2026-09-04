export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const envApiUrl = process.env.NEXT_PUBLIC_API_URL;
  // If NEXT_PUBLIC_API_URL is set (e.g. http://localhost:8000), use that host
  const base = envApiUrl ? envApiUrl.replace(/\/+$/, '') : '';
  
  // Ensure path starts with /api if it doesn't already
  let cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (!cleanPath.startsWith('/api')) {
    cleanPath = `/api${cleanPath}`;
  }

  const url = `${base}${cleanPath}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch (_) {}
    throw new Error(`API Error (${response.status}): ${errorDetail}`);
  }

  return response.json();
}
