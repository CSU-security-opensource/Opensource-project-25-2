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
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const PowerPlantDashboard = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  // 발전소 데이터
  const powerPlants = [
    {
      id: 1,
      name: "한림 태양광 발전소",
      location: "제주시 한림읍",
      type: "태양광",
      capacity: 45.2,
      utilization: 92.3,
      status: "운영중",
      operator: "제주에너지",
    },
    {
      id: 2,
      name: "성산 풍력 발전소",
      location: "서귀포시 성산읍",
      type: "풍력",
      capacity: 78.5,
      utilization: 87.1,
      status: "운영중",
      operator: "제주풍력",
    },
    {
      id: 3,
      name: "제주 화력 발전소",
      location: "제주시 애월읍",
      type: "화력",
      capacity: 200.0,
      utilization: 94.7,
      status: "운영중",
      operator: "한국남동발전",
    },
    {
      id: 4,
      name: "표선 태양광 발전소",
      location: "서귀포시 표선면",
      type: "태양광",
      capacity: 38.4,
      utilization: 89.2,
      status: "운영중",
      operator: "제주에너지",
    },
    {
      id: 5,
      name: "월정 풍력 발전소",
      location: "제주시 구좌읍",
      type: "풍력",
      capacity: 42.0,
      utilization: 85.6,
      status: "운영중",
      operator: "제주풍력",
    },
    {
      id: 6,
      name: "김녕 풍력 발전소",
      location: "제주시 구좌읍",
      type: "풍력",
      capacity: 15.0,
      utilization: 88.9,
      status: "운영중",
      operator: "제주풍력",
    },
    {
      id: 7,
      name: "중문 수력 발전소",
      location: "서귀포시 중문동",
      type: "수력",
      capacity: 12.5,
      utilization: 76.3,
      status: "운영중",
      operator: "한국수자원공사",
    },
    {
      id: 8,
      name: "신창 풍력 발전소",
      location: "제주시 한경면",
      type: "풍력",
      capacity: 99.0,
      utilization: 91.4,
      status: "운영중",
      operator: "제주풍력",
    },
    {
      id: 9,
      name: "애월 태양광 발전소",
      location: "제주시 애월읍",
      type: "태양광",
      capacity: 25.6,
      utilization: 90.1,
      status: "운영중",
      operator: "제주에너지",
    },
    {
      id: 10,
      name: "서귀포 화력 발전소",
      location: "서귀포시 대정읍",
      type: "화력",
      capacity: 150.0,
      utilization: 93.2,
      status: "운영중",
      operator: "한국남동발전",
    },
  ];

  // 발전소 유형별 아이콘
  const getTypeIcon = (type) => {
    switch (type) {
      case "태양광":
        return <Sun className="w-8 h-8" />;
      case "풍력":
        return <Wind className="w-8 h-8" />;
      case "화력":
        return <Flame className="w-8 h-8" />;
      case "수력":
        return <Droplets className="w-8 h-8" />;
      default:
        return null;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case "태양광":
        return "bg-yellow-50 text-yellow-600";
      case "풍력":
        return "bg-blue-50 text-blue-600";
      case "화력":
        return "bg-red-50 text-red-600";
      case "수력":
        return "bg-cyan-50 text-cyan-600";
      default:
        return "bg-gray-50 text-gray-600";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">Logo</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-900">
              에너지 모니터링 시스템
            </h1>
          </div>
          <nav className="flex gap-8">
            <button
              onClick={() => onNavigate && onNavigate("dashboard")}
              className="text-gray-600 hover:text-gray-900"
            >
              홈
            </button>
            <button className="text-teal-500 font-semibold">발전소 현황</button>
            <button className="text-gray-600 hover:text-gray-900">
              데이터 분석
            </button>
            <button className="text-gray-600 hover:text-gray-900">설정</button>
          </nav>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Title */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            제주도 발전소 현황
          </h2>
          <p className="text-gray-600">
            제주도 지역의 모든 발전소 정보와 설비용량을 확인하세요
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600 font-medium">전체 발전소</span>
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">47개소</div>
            <div className="text-sm text-blue-600">+3개소 전년 대비</div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600 font-medium">총 설비용량</span>
              <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              1,847 MW
            </div>
            <div className="text-sm text-green-600">+147 MW 전년 대비</div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600 font-medium">평균 가동률</span>
              <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">87.4%</div>
            <div className="text-sm text-orange-600">+2.1% 전월 대비</div>
          </div>
        </div>

        {/* Energy Type Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-yellow-50 rounded-full flex items-center justify-center text-yellow-600">
                <Sun className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm text-gray-600">태양광</div>
                <div className="text-xs text-gray-500">Solar Power</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">발전소 수</span>
                <span className="font-semibold">23개소</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">설비용량</span>
                <span className="font-semibold">487 MW</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">점유율</span>
                <span className="font-semibold text-yellow-600">26.4%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                <Wind className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm text-gray-600">풍력</div>
                <div className="text-xs text-gray-500">Wind Power</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">발전소 수</span>
                <span className="font-semibold">12개소</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">설비용량</span>
                <span className="font-semibold">634 MW</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">점유율</span>
                <span className="font-semibold text-blue-600">34.3%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center text-red-600">
                <Flame className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm text-gray-600">화력</div>
                <div className="text-xs text-gray-500">Thermal Power</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">발전소 수</span>
                <span className="font-semibold">8개소</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">설비용량</span>
                <span className="font-semibold">592 MW</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">점유율</span>
                <span className="font-semibold text-red-600">32.1%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-cyan-50 rounded-full flex items-center justify-center text-cyan-600">
                <Droplets className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm text-gray-600">수력</div>
                <div className="text-xs text-gray-500">Hydro Power</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">발전소 수</span>
                <span className="font-semibold">4개소</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">설비용량</span>
                <span className="font-semibold">134 MW</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">점유율</span>
                <span className="font-semibold text-cyan-600">7.2%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Map and Chart Section */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              발전소 위치 현황
            </h3>
            <div className="bg-gray-100 rounded-lg h-80 flex items-center justify-center relative">
              <div className="absolute top-4 left-4 bg-white px-4 py-2 rounded-lg shadow-sm">
                <div className="text-sm font-semibold">제주도 발전소 분포</div>
                <div className="text-xs text-gray-600">총 47개소</div>
              </div>
              <div className="text-gray-400 flex flex-col items-center gap-2">
                <Building2 className="w-16 h-16" />
                <span className="text-sm">지도 영역</span>
              </div>
              <div className="absolute bottom-4 right-4 flex gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <span>태양광</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span>풍력</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span>화력</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                  <span>수력</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              에너지원별 점유율
            </h3>
            <div className="flex items-center justify-center h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: "풍력", value: 34.3, color: "#3b82f6" },
                      { name: "화력", value: 32.1, color: "#ef4444" },
                      { name: "태양광", value: 26.4, color: "#eab308" },
                      { name: "수력", value: 7.2, color: "#06b6d4" },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: "풍력", value: 34.3, color: "#3b82f6" },
                      { name: "화력", value: 32.1, color: "#ef4444" },
                      { name: "태양광", value: 26.4, color: "#eab308" },
                      { name: "수력", value: 7.2, color: "#06b6d4" },
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Power Plants Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              발전소 상세 목록
            </h3>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="발전소명 검색"
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">
                <Filter className="w-4 h-4" />
                필터
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    발전소명
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    위치
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    유형
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    설비용량
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    가동률
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                    상태
                  </th>
                </tr>
              </thead>
              <tbody>
                {powerPlants
                  .filter((plant) =>
                    plant.name.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .slice(
                    (currentPage - 1) * itemsPerPage,
                    currentPage * itemsPerPage
                  )
                  .map((plant) => (
                    <tr
                      key={plant.id}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium text-gray-900">
                            {plant.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            운영사: {plant.operator}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-600">
                        {plant.location}
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(
                            plant.type
                          )}`}
                        >
                          {plant.type}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-sm font-medium text-gray-900">
                        {plant.capacity} MW
                      </td>
                      <td className="py-4 px-4 text-sm font-medium text-gray-900">
                        {plant.utilization}%
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            plant.status === "운영중"
                              ? "bg-green-50 text-green-600"
                              : "bg-yellow-50 text-yellow-600"
                          }`}
                        >
                          {plant.status}
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6 p-6">
            <div className="text-sm text-gray-600">
              총{" "}
              {
                powerPlants.filter((plant) =>
                  plant.name.toLowerCase().includes(searchTerm.toLowerCase())
                ).length
              }
              개 중{" "}
              {Math.min(
                (currentPage - 1) * itemsPerPage + 1,
                powerPlants.filter((plant) =>
                  plant.name.toLowerCase().includes(searchTerm.toLowerCase())
                ).length
              )}
              -
              {Math.min(
                currentPage * itemsPerPage,
                powerPlants.filter((plant) =>
                  plant.name.toLowerCase().includes(searchTerm.toLowerCase())
                ).length
              )}
              개 표시
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-4 py-2 text-sm text-gray-600">
                {currentPage} /{" "}
                {Math.ceil(
                  powerPlants.filter((plant) =>
                    plant.name.toLowerCase().includes(searchTerm.toLowerCase())
                  ).length / itemsPerPage
                )}
              </span>
              <button
                onClick={() =>
                  setCurrentPage(
                    Math.min(
                      Math.ceil(
                        powerPlants.filter((plant) =>
                          plant.name
                            .toLowerCase()
                            .includes(searchTerm.toLowerCase())
                        ).length / itemsPerPage
                      ),
                      currentPage + 1
                    )
                  )
                }
                disabled={
                  currentPage ===
                  Math.ceil(
                    powerPlants.filter((plant) =>
                      plant.name
                        .toLowerCase()
                        .includes(searchTerm.toLowerCase())
                    ).length / itemsPerPage
                  )
                }
                className="p-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PowerPlantDashboard;
