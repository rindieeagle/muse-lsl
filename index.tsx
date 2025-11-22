import App from "./src/App";
import { createRoot } from "react-dom/client";
import "./src/theme.css";

// Load DOM inspector immediately
import("./src/visual-inspector.js").catch(()=>{});

const root = createRoot(document.getElementById("root")!);
root.render(<App />);