export const getApiUrl = (path: string): string => {
  const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  return `http://${hostname}:8000${path.startsWith('/') ? path : '/' + path}`;
};
