import Header from "./Header";
import { Outlet } from "react-router-dom";
import {
  CssBaseline,
  PaletteMode,
  ThemeProvider,
  createTheme,
} from "@mui/material";
import { useState } from "react";
export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const theme: PaletteMode = darkMode ? "dark" : "light";
  const darkTheme = createTheme({
    palette: {
      mode: theme,
    },
  });
    return (
        <ThemeProvider theme={darkTheme}>
          <CssBaseline />
          <Header />
          <Outlet/>
        </ThemeProvider>
    );
}