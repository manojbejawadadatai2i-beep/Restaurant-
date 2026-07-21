export const getApiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : '/' + path;
  return `/api/proxy${cleanPath}`;
};
