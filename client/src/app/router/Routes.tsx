import { createBrowserRouter } from "react-router-dom";
import App from "../layout/App";
import SearchAndTags from "../../features/Search/SearchAndTags";
import Quiz from "../../features/Q&A/Quiz";
export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "search",
        element: <SearchAndTags />,
      },
      {
        path: "quiz",
        element: <Quiz />,
      },
    ],
  },
]);
