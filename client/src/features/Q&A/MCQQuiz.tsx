import React, { useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Button,
  Box,
} from "@mui/material";
import { Link } from "react-router-dom";

interface Question {
  question: string;
  options: string[];
  correct_option: string;
  explanation: string;
}

interface MCQQuizProps {
  questions: Question[];
}

const MCQQuiz: React.FC<MCQQuizProps> = ({ questions }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];

  const handleOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedOption(event.target.value);
  };

  const handleSubmit = () => {
    if (selectedOption) {
      setShowExplanation(true);
      if (selectedOption === currentQuestion.correct_option) {
        setCorrectAnswers((prev) => prev + 1);
      }
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setSelectedOption(null);
      setShowExplanation(false);
    } else {
      setQuizCompleted(true);
    }
  };

  const handleRestartQuiz = () => {
    setCurrentQuestionIndex(0);
    setSelectedOption(null);
    setShowExplanation(false);
    setCorrectAnswers(0);
    setQuizCompleted(false);
  };
  if (questions.length === 0) {
    return (
      <Card sx={{ maxWidth: 600, margin: "auto", mt: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            No questions found
          </Typography>
          <Typography variant="body1" paragraph>
            Please check your search query and try again.
          </Typography>
          <Box mt={2} display="flex" justifyContent="space-between">
            <Button
              variant="contained"
              color="secondary"
              component={Link}
              to="/search"
            >
              Back to Search
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }
  if (quizCompleted) {
    return (
      <Card sx={{ maxWidth: 600, margin: "auto", mt: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Quiz Completed!
          </Typography>
          <Typography variant="body1" paragraph>
            You answered {correctAnswers} out of {questions.length} questions
            correctly.
          </Typography>
          <Box mt={2} display="flex" justifyContent="space-between">
            <Button
              variant="contained"
              color="primary"
              onClick={handleRestartQuiz}
            >
              Restart Quiz
            </Button>
            <Button
              variant="contained"
              color="secondary"
              component={Link}
              to="/search"
            >
              Back to Search
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ maxWidth: 600, margin: "auto", mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Question {currentQuestionIndex + 1} of {questions.length}
        </Typography>
        <Typography variant="body1" paragraph>
          {currentQuestion.question}
        </Typography>
        <RadioGroup value={selectedOption} onChange={handleOptionChange}>
          {currentQuestion.options.map((option, index) => (
            <FormControlLabel
              key={index}
              value={option}
              control={<Radio />}
              label={option}
            />
          ))}
        </RadioGroup>
        <Box mt={2} display="flex" justifyContent="space-between">
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={!selectedOption || showExplanation}
          >
            Submit
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={handleNext}
            disabled={!showExplanation}
          >
            {currentQuestionIndex < questions.length - 1 ? "Next" : "Finish"}
          </Button>
        </Box>
        {showExplanation && (
          <Box mt={2}>
            <Typography
              variant="body1"
              color={
                selectedOption === currentQuestion.correct_option
                  ? "success.main"
                  : "error.main"
              }
            >
              {selectedOption === currentQuestion.correct_option
                ? "Correct!"
                : "Incorrect."}
            </Typography>
            <Typography variant="body2" mt={1}>
              Explanation: {currentQuestion.explanation}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default MCQQuiz;
