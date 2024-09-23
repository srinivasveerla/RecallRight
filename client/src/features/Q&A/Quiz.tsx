import { useLocation } from "react-router-dom";
import MCQQuiz from "./MCQQuiz";
import { useEffect, useState } from "react";
import agent from "../../app/api/agent";

type Question = {
  question: string;
  options: string[];
  correct_option: string;
  explanation: string;
};
export default function Quiz() {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const location = useLocation();
  useEffect(() => {
    const query = location.state?.searchQuery || location.state?.selectedTag;
    agent.Questions.list(query)
      .then((response) => setQuestions(response))
      .catch((err) => console.log(err))
      .finally(() => {
        setLoading(false);
        console.log(questions);
      });
  }, [location.state]);
  return loading ? "Loading..." : <MCQQuiz questions={questions} />;
}
