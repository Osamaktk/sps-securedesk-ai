const DEFAULT_DELAY = 120;

export function cloneMockData(data) {
  return data === undefined ? undefined : JSON.parse(JSON.stringify(data));
}

export function mockApiResponse(data, delay = DEFAULT_DELAY) {
  return new Promise((resolve) => {
    globalThis.setTimeout(() => resolve(cloneMockData(data)), delay);
  });
}

export function mockApiError(message, code = 'MOCK_API_ERROR', delay = DEFAULT_DELAY) {
  return new Promise((_, reject) => {
    globalThis.setTimeout(() => {
      const error = new Error(message);
      error.code = code;
      reject(error);
    }, delay);
  });
}

const api = {
  get: (data) => mockApiResponse(data),
  post: (data) => mockApiResponse(data),
  patch: (data) => mockApiResponse(data),
  delete: (data) => mockApiResponse(data),
};

export default api;
