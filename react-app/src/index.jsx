import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import "@fontsource-variable/bricolage-grotesque/wght.css";
import "@fontsource-variable/figtree/wght.css";
import "./styles/tokens.css";
import "./styles/base.css";
import App from "./App";
import configureStore from "./store";

const store = configureStore();

// React 18+ API (ReactDOM.render was removed in React 19).
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
