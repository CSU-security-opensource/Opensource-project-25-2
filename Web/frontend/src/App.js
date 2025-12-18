import React, { useState } from "react";
import Header from "./components/Header";
import Home from "./pages/Home";
import PowerPlant from "./pages/PowerPlant";
import Analysis from "./pages/Analysis";
import Settings from "./pages/Settings";
import { ThemeProvider } from "./context/ThemeContext";

function App() {
  const [currentView, setCurrentView] = useState("analysis");

  const renderContent = () => {
    switch (currentView) {
      case "home":
        return <Home onNavigate={setCurrentView} />;
      case "powerplant":
        return <PowerPlant />;
      case "analysis":
        return <Analysis />;
      case "settings":
        return <Settings />;
      default:
        return <Analysis />;
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-200">
        <Header onNavigate={setCurrentView} currentView={currentView} />
        <main>
          {renderContent()}
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;