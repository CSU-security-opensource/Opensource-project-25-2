import React, { useState } from "react";
import {
  Building2,
  TrendingUp,
  Clock,
  Sun,
  Wind,
  Flame,
  Droplets,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Eye,
  Settings,
  Activity,
  AlertCircle
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const PowerPlantDashboard = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const itemsPerPage = 8; // Increased for grid view

  // 발전소 데이터 (Updated with Daily Generation)
  const powerPlants = [
    {
      id: 1,
      name: "제주동부 태양광 1호기",
      location: "제주시 구좌읍",
      type: "태양광",
      capacity: 3.5,
      utilization: 94.2,
      dailyGen: 68.4,
      status: "정상",
      operator: "제주에너지",
    },
    {
      id: 2,
      name: "제주서부 풍력 1호기",
      location: "제주시 한림읍",
      type: "풍력",
      capacity: 2.8,
      utilization: 91.8,
      dailyGen: 52.3,
      status: "정상",
      operator: "제주풍력",
    },
    {
      id: 3,
      name: "서귀포 태양광 2호기",
      location: "서귀포시 안덕면",
      type: "태양광",
      capacity: 4.2,
      utilization: 96.1,
      dailyGen: 78.9,
      status: "정상",
      operator: "한국남동발전",
    },
    {
      id: 4,
      name: "제주남부 풍력 2호기",
      location: "서귀포시 성산읍",
      type: "풍력",
      capacity: 3.1,
      utilization: 89.5,
      dailyGen: 45.2,
      status: "점검중",
      operator: "제주에너지",
    },
    {
      id: 5,
      name: "한림 태양광 3호기",
      location: "제주시 한림읍",
      type: "태양광",
      capacity: 45.2,
      utilization: 92.3,
      dailyGen: 812.5,
      status: "정상",
      operator: "제주에너지",
    },
    {
      id: 6,
      name: "성산 풍력 3호기",
      location: "서귀포시 성산읍",
      type: "풍력",
      capacity: 78.5,
      utilization: 87.1,
      dailyGen: 1205.3,
      status: "정상",
      operator: "제주풍력",
    },
    {
      id: 7,
      name: "중문 태양광 4호기",
      location: "서귀포시 중문동",
      type: "태양광",
      capacity: 12.5,
      utilization: 76.3,
      dailyGen: 210.4,
      status: "정상",
      operator: "한국수자원공사",
    },
    {
      id: 8,
      name: "표선 풍력 4호기",
      location: "서귀포시 표선면",
      type: "풍력",
      capacity: 99.0,
      utilization: 91.4,
      dailyGen: 1850.2,
      status: "정상",
      operator: "제주풍력",
    },
    {
      id: 9,
      name: "애월 태양광 5호기",
      location: "제주시 애월읍",
      type: "태양광",
      capacity: 25.6,
      utilization: 90.1,
      dailyGen: 450.1,
      status: "정상",
      operator: "제주에너지",
    },
    {
      id: 10,
      name: "대정 풍력 5호기",
      location: "서귀포시 대정읍",
      type: "풍력",
      capacity: 150.0,
      utilization: 93.2,
      dailyGen: 2890.5,
      status: "점검중",
      operator: "한국남동발전",
    },
  ];

  // Utility functions
  const getTypeIcon = (type) => {
    switch (type) {
      case "태양광": return <Sun className="w-5 h-5" />;
      case "풍력": return <Wind className="w-5 h-5" />;
      case "화력": return <Flame className="w-5 h-5" />;
      case "수력": return <Droplets className="w-5 h-5" />;
      default: return null;
    }
  };

  const getStatusColor = (status) => {
    return status === "정상"
      ? "bg-green-50 text-green-600 border-green-100"
      : "bg-yellow-50 text-yellow-600 border-yellow-100";
  };

  const getTypeColor = (type) => {
    switch (type) {
      case "태양광": return "text-yellow-500 bg-yellow-50";
      case "풍력": return "text-blue-500 bg-blue-50";
      default: return "text-gray-500 bg-gray-50";
    }
  };

  // Filtered Data
  const filteredPlants = powerPlants.filter((plant) =>
    plant.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredPlants.length / itemsPerPage);
  const currentPlants = filteredPlants.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );


  // Stats Calculation
  const totalCount = powerPlants.length;
  const solarCount = powerPlants.filter(p => p.type === "태양광").length;
  const windCount = powerPlants.filter(p => p.type === "풍력").length;
  const normalCount = powerPlants.filter(p => p.status === "정상").length;
  const maintenanceCount = powerPlants.filter(p => p.status === "점검중").length;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <button onClick={() => onNavigate && onNavigate("dashboard")} className="hidden md:flex items-center text-gray-500 hover:text-gray-900">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xs">logo</span>
              </div>
              <h1 className="text-lg font-bold text-gray-900 hidden sm:block">
                발전소 현황
              </h1>
            </div>

            {/* Desktop Nav */}
            <nav className="hidden md:flex gap-8 text-sm font-medium">
              <button onClick={() => onNavigate && onNavigate("dashboard")} className="text-gray-500 hover:text-gray-900">홈</button>
              <button className="text-green-600">발전소 현황</button>
              <button className="text-gray-500 hover:text-gray-900">데이터 분석</button>
              <button className="text-gray-500 hover:text-gray-900">설정</button>
            </nav>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-gray-600"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100">
            <div className="px-4 pt-2 pb-4 space-y-1">
              <button onClick={() => onNavigate && onNavigate("dashboard")} className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-50">홈</button>
              <button className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-green-600 bg-green-50">발전소 현황</button>
              <button className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-50">데이터 분석</button>
              <button className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-50">설정</button>
            </div>
          </div>
        )}
      </header>

      <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* Top Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
          {/* Card 1: Total */}
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-start justify-between mb-2">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
              <span className="text-xs font-medium text-gray-400">전체</span>
            </div>
            <div className="text-gray-600 text-sm font-medium mb-1">전체 발전소</div>
            <div className="text-2xl font-bold text-blue-600">{totalCount}</div>
          </div>

          {/* Card 2: Solar */}
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-start justify-between mb-2">
              <div className="p-2 bg-yellow-50 rounded-lg">
                <Sun className="w-5 h-5 text-yellow-600" />
              </div>
              <span className="text-xs font-medium text-gray-400">태양광</span>
            </div>
            <div className="text-gray-600 text-sm font-medium mb-1">태양광</div>
            <div className="text-2xl font-bold text-yellow-600">{solarCount}</div>
          </div>

          {/* Card 3: Wind */}
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-start justify-between mb-2">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Wind className="w-5 h-5 text-blue-500" />
              </div>
              <span className="text-xs font-medium text-gray-400">풍력</span>
            </div>
            <div className="text-gray-600 text-sm font-medium mb-1">풍력</div>
            <div className="text-2xl font-bold text-blue-600">{windCount}</div>
          </div>

          {/* Card 4: Normal */}
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-start justify-between mb-2">
              <div className="p-2 bg-green-50 rounded-lg">
                <Activity className="w-5 h-5 text-green-600" />
              </div>
              <span className="text-xs font-medium text-gray-400">가동중</span>
            </div>
            <div className="text-gray-600 text-sm font-medium mb-1">정상 운영</div>
            <div className="text-2xl font-bold text-green-600">{normalCount}</div>
          </div>

          {/* Card 5: Maintenance */}
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 col-span-2 md:col-span-1 lg:col-span-1">
            <div className="flex items-start justify-between mb-2">
              <div className="p-2 bg-orange-50 rounded-lg">
                <AlertCircle className="w-5 h-5 text-orange-600" />
              </div>
              <span className="text-xs font-medium text-gray-400">보수 필요</span>
            </div>
            <div className="text-gray-600 text-sm font-medium mb-1">점검중</div>
            <div className="text-2xl font-bold text-orange-600">{maintenanceCount}</div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-8 flex flex-col md:flex-row gap-4 justify-between items-center">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="발전소명 또는 위치로 검색..."
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:bg-white transition-colors"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>
          <div className="flex gap-3 w-full md:w-auto">
            <select className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer">
              <option>전체 유형</option>
              <option>태양광</option>
              <option>풍력</option>
            </select>
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm">
              <Filter className="w-4 h-4" />
              필터
            </button>
          </div>
        </div>

        {/* Power Plant Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
          {currentPlants.map((plant) => (
            <div key={plant.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col">
              <div className="flex justify-between items-start mb-4">
                <div className="flex gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getTypeColor(plant.type)}`}>
                    {getTypeIcon(plant.type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-sm">{plant.name}</h3>
                    <div className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-gray-400"></span>
                      {plant.location}
                    </div>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-bold border ${getStatusColor(plant.status)}`}>
                  {plant.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <span className="block text-xs text-gray-500 mb-1">설비 용량</span>
                  <span className="block text-sm font-bold text-gray-900">{plant.capacity}MW</span>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <span className="block text-xs text-gray-500 mb-1">발전 효율</span>
                  <span className="block text-sm font-bold text-gray-900">{plant.utilization}%</span>
                </div>
              </div>

              <div className="mt-auto">
                <div className="bg-blue-50 p-4 rounded-xl mb-4">
                  <span className="block text-xs text-blue-600 font-medium mb-1">오늘 발전량</span>
                  <span className="block text-xl font-bold text-blue-700">{plant.dailyGen}MWh</span>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors">
                    <Eye className="w-4 h-4" />
                    상세 보기
                  </button>
                  <button className="px-3 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 0 && (
          <div className="flex justify-center items-center gap-2 mt-auto">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex gap-1">
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium ${currentPage === i + 1
                      ? "bg-blue-600 text-white"
                      : "text-gray-600 hover:bg-gray-50"
                    }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default PowerPlantDashboard;
