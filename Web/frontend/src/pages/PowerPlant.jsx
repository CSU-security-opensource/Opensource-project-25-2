import React, { useState } from "react";
import {
    Building2,
    Clock,
    Sun,
    Wind,
    Flame,
    Droplets,
    Search,
    Filter,
    ChevronLeft,
    ChevronRight,
    Eye,
    Settings,
    Activity,
    AlertCircle
} from "lucide-react";

// ✅ [수정 1] props로 onNavigateToAnalysis 함수를 받습니다.
const PowerPlant = ({ onNavigateToAnalysis }) => {
    const [searchTerm, setSearchTerm] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 8; // Increased for grid view

    // 발전소 데이터 (Updated with Daily Generation)
    const powerPlants = [
        {
            id: 1,
            name: "제주중앙 태양광발전소",
            location: "제주특별자치도 서귀포시 성산읍 신풍리 347-1번지",
            type: "태양광",
            capacity: 83.18,
            utilization: 0.0,
            dailyGen: 83.18,
            status: "정상",
            operator: "제주에너지",
        },
        {
            id: 2,
            name: "수망 태양광발전시설",
            location: "서귀포시 남원읍 수망리",
            type: "태양광",
            capacity: 83.184,
            utilization: 0.1,
            dailyGen: 83.18,
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
            ? "bg-green-50 text-green-600 border-green-100 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800"
            : "bg-yellow-50 text-yellow-600 border-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800";
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
        <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
            {/* Top Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
                {/* Card 1: Total */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                            <Building2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <span className="text-xs font-medium text-gray-400">전체</span>
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">전체 발전소</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totalCount}</div>
                </div>

                {/* Card 2: Solar */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg">
                            <Sun className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                        </div>
                        <span className="text-xs font-medium text-gray-400">태양광</span>
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">태양광</div>
                    <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{solarCount}</div>
                </div>

                {/* Card 3: Wind */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                            <Wind className="w-5 h-5 text-blue-500 dark:text-blue-400" />
                        </div>
                        <span className="text-xs font-medium text-gray-400">풍력</span>
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">풍력</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{windCount}</div>
                </div>

                {/* Card 4: Normal */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-green-50 dark:bg-green-900/30 rounded-lg">
                            <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <span className="text-xs font-medium text-gray-400">가동중</span>
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">정상 운영</div>
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">{normalCount}</div>
                </div>

                {/* Card 5: Maintenance */}
                <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 col-span-2 md:col-span-1 lg:col-span-1">
                    <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-orange-50 dark:bg-orange-900/30 rounded-lg">
                            <AlertCircle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        </div>
                        <span className="text-xs font-medium text-gray-400">보수 필요</span>
                    </div>
                    <div className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">점검중</div>
                    <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{maintenanceCount}</div>
                </div>
            </div>

            {/* Search & Filter Bar */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-8 flex flex-col md:flex-row gap-4 justify-between items-center transition-colors duration-200">
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="발전소명 또는 위치로 검색..."
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:bg-white dark:focus:bg-gray-600 transition-colors"
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setCurrentPage(1);
                        }}
                    />
                </div>
                <div className="flex gap-3 w-full md:w-auto">
                    <select className="px-4 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer">
                        <option>전체 유형</option>
                        <option>태양광</option>
                        <option>풍력</option>
                    </select>
                    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm">
                        <Filter className="w-4 h-4" />
                        필터
                    </button>
                </div>
            </div>

            {/* Power Plant Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
                {currentPlants.map((plant) => (
                    <div key={plant.id} className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex gap-3 overflow-hidden">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${getTypeColor(plant.type)}`}>
                                    {getTypeIcon(plant.type)}
                                </div>
                                <div className="min-w-0">
                                    <h3 className="font-bold text-gray-900 dark:text-white text-sm whitespace-nowrap truncate">{plant.name}</h3>
                                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 flex items-center gap-1">
                                        <span className="w-1 h-1 rounded-full bg-gray-400"></span>
                                        {plant.location}
                                    </div>
                                </div>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-bold border whitespace-nowrap shrink-0 ml-2 ${getStatusColor(plant.status)}`}>
                                {plant.status}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                                <span className="block text-xs text-gray-500 dark:text-gray-400 mb-1">설비 용량</span>
                                <span className="block text-sm font-bold text-gray-900 dark:text-white">{plant.capacity}MW</span>
                            </div>
                            <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                                <span className="block text-xs text-gray-500 dark:text-gray-400 mb-1">발전 효율</span>
                                <span className="block text-sm font-bold text-gray-900 dark:text-white">{plant.utilization}%</span>
                            </div>
                        </div>

                        <div className="mt-auto">
                            <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-xl mb-4">
                                <span className="block text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">오늘 발전량</span>
                                <span className="block text-xl font-bold text-blue-700 dark:text-blue-300">{plant.dailyGen}MWh</span>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    // ✅ [수정 2] 클릭 시 App.js의 함수를 실행하여 plant.id를 전달
                                    onClick={() => onNavigateToAnalysis(plant.id)}
                                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                                >
                                    <Eye className="w-4 h-4" />
                                    상세 보기
                                </button>
                                <button className="px-3 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-lg transition-colors">
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
                        className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
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
                                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                                    }`}
                            >
                                {i + 1}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            )}
        </div>
    );
};

export default PowerPlant;