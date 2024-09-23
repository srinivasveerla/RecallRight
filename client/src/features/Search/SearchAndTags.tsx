import {
  Container,
  Paper,
  TextField,
  FormGroup,
  FormControlLabel,
  Radio,
  RadioGroup,
  Button,
} from "@mui/material";
import agent from "../../app/api/agent";
import { useState, useEffect, FormEvent, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";

export default function SearchAndTags() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedTag, setSelectedTag] = useState<string>(""); // Single selected tag
  const [tags, setTags] = useState<string[]>([]);
  const navigate = useNavigate();

  // Fetch tags from the API when the component mounts
  useEffect(() => {
    agent.Tags.list().then((response) => setTags(response.tags));
  }, []);

  const handleSearchSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (searchQuery) {
      navigate(`/quiz`, { state: { searchQuery } });
    } else if (selectedTag) {
      navigate(`/quiz`, { state: { selectedTag } });
    }
  };

  const handleTagChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSelectedTag(event.target.value); // Only one tag can be selected
  };

  const handleSearchInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <form onSubmit={handleSearchSubmit}>
            {/* Search Input */}
            <TextField
              fullWidth
              variant="outlined"
              label="Search"
              value={searchQuery}
              onChange={handleSearchInputChange}
              sx={{ mb: 2 }}
            />

            {/* Tag Radio Buttons */}
            <FormGroup>
              <RadioGroup
                value={selectedTag}
                onChange={handleTagChange}
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  flexWrap: "wrap",
                  justifyContent: "center",
                }}
              >
                {tags.map((tag) => (
                  <FormControlLabel
                    key={tag}
                    control={
                      <Radio
                        value={tag}
                        disabled={searchQuery.length > 0}
                      />
                    }
                    label={tag.replace(/^\s*(\w)/, (match) =>
                      match.toUpperCase()
                    )}
                  />
                ))}
              </RadioGroup>
            </FormGroup>

            {/* Submit Button */}
            <Button variant="contained" type="submit">
              Go
            </Button>
          </form>
        </Paper>
      </Container>
    </div>
  );
}
