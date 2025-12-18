import React, { useState } from "react";
import SolarMonitoringDashboard from "./solar-monitoring-dashboard-updated";
import PowerPlantDashboard from "./발전소-updated";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("dashboard");

  const navigateTo = (view) => {
    setCurrentView(view);
  };

  return (
    <div className="App">
      {currentView === "dashboard" && (
        <SolarMonitoringDashboard onNavigate={navigateTo} />
      )}
      {currentView === "powerplant" && (
        <PowerPlantDashboard onNavigate={navigateTo} />
      )}
    </div>
  );
}

export default App;
