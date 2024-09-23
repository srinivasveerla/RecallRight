import axios, { AxiosError, AxiosResponse } from "axios";
axios.defaults.baseURL = "http://127.0.0.1:8000/api/";
// axios.defaults.withCredentials = true;

const responseBody = (response: AxiosResponse) => response.data;

axios.interceptors.response.use(
  async (response) => {
    return response;
  },
  (error: AxiosError) => {
    return Promise.reject(error.response);
  }
);

const requests = {
  get: (url: string) => axios.get(url).then(responseBody),
  post: (url: string, body: object) => axios.post(url, body).then(responseBody),
  put: (url: string, body: object) => axios.put(url, body).then(responseBody),
  delete: (url: string) => axios.delete(url).then(responseBody),
};

const Questions = {
  /**
   * Given a query, returns up to 10 questions that match the query.
   *
   * @param {string} query - Query to search for.
   * @returns {Promise<Question[]>} - Promise of a list of questions.
   */
  list: (query: string) =>
    requests.post("questionsBySearchQuery", {
      query: query,
      questions: 10,
    }),
};
const Tags = {
  list: () => requests.get("tags"),
};

const agent = {
  Questions,
  Tags,
};

export default agent;
