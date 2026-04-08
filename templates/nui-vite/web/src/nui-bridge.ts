const IS_BROWSER = !(window as any).GetParentResourceName;

export function useNuiEvent<T = any>(action: string, handler: (data: T) => void) {
  const listener = (event: MessageEvent) => {
    if (event.data?.action === action) {
      handler(event.data as T);
    }
  };
  window.addEventListener('message', listener);
  return () => window.removeEventListener('message', listener);
}

export async function fetchNui<T = any>(event: string, data?: Record<string, any>): Promise<T> {
  if (IS_BROWSER) {
    return new Promise((resolve) => {
      setTimeout(() => resolve({} as T), 200);
    });
  }

  const resourceName = (window as any).GetParentResourceName();
  const resp = await fetch(`https://${resourceName}/${event}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data ?? {}),
  });
  return resp.json();
}

export function closeNui() {
  fetchNui('close');
}
