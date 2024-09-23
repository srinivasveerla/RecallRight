import { AppBar, Toolbar, Typography } from "@mui/material";
import { Link } from "react-router-dom";
export default function Header() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={Link} to="/search" sx={{ flexGrow: 1, textDecoration: "none", color: "inherit" }}>
          RecallRight
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
