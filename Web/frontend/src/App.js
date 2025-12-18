import React, { useState } from "react";
import Header from "./components/Header";
import Home from "./pages/Home";
import PowerPlant from "./pages/PowerPlant";
import Analysis from "./pages/Analysis";
import Settings from "./pages/Settings";
import { ThemeProvider } from "./context/ThemeContext";

function App() {
  const [currentView, setCurrentView] = useState("analysis");
  // [추가] 선택된 발전소 ID 상태 (기본값 1)
  const [selectedPlantId, setSelectedPlantId] = useState(1);

  // [추가] 발전소 상세 보기로 이동하는 함수
  const goToAnalysis = (plantId) => {
    setSelectedPlantId(plantId);
    setCurrentView("analysis");
  };

  const renderContent = () => {
    switch (currentView) {
      case "home":
        return <Home onNavigate={setCurrentView} />;
      case "powerplant":
        // [수정] goToAnalysis 함수를 props로 전달
        return <PowerPlant onNavigateToAnalysis={goToAnalysis} />;
      case "analysis":
        // [수정] 선택된 plantId를 props로 전달
        return <Analysis plantId={selectedPlantId} />;
      case "settings":
        return <Settings />;
      default:
        return <Analysis plantId={selectedPlantId} />;
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