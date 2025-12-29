import React, { useState, useEffect } from "react";
import {
    Sun,
    Cloud,
    Thermometer,
    Activity,
    TrendingUp,
    Battery,
    AlertCircle,
} from "lucide-react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart,
} from "recharts";

const Analysis = () => {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // 시간별 발전량 데이터
    const hourlyData = [
        { time: "00", power: 0 },
        { time: "02", power: 0 },
        { time: "04", power: 50 },
        { time: "06", power: 500 },
        { time: "08", power: 1500 },
        { time: "10", power: 2400 },
        { time: "12", power: 3100 },
        { time: "14", power: 3200 },
        { time: "16", power: 2800 },
        { time: "18", power: 1800 },
        { time: "20", power: 400 },
        { time: "22", power: 0 },
    ];

    // 일별 발전량 데이터 (최근 30일)
    const dailyData = Array.from({ length: 30 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (29 - i));
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        const baseValue = isWeekend ? 48000 : 50000;
        return {
            date: `${date.getMonth() + 1}/${date.getDate()}일`,
            actual: Math.floor(baseValue + Math.random() * 4000 - 2000),
            average: 50000,
            isToday: i === 29,
        };
    });

    const StatCard = ({
        title,
        value,
        unit,
        change,
        icon: Icon,
        color = "blue",
    }) => (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-${color}-50 dark:bg-gray-700`}>
                    <Icon className={`w-6 h-6 text-${color}-500 dark:text-${color}-400`} />
                </div>
                {change && (
                    <span
                        className={`text-sm font-semibold ${change > 0 ? "text-green-500" : "text-red-500"
                            }`}
                    >
                        {change > 0 ? "+" : ""}
                        {change}%
                    </span>
                )}
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">{title}</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {value}
                <span className="text-lg font-normal text-gray-600 dark:text-gray-400 ml-1">{unit}</span>
            </p>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-8 pt-8 transition-colors duration-200">

            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
                <div className="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-800 dark:to-blue-600 rounded-3xl p-8 relative overflow-hidden shadow-lg">
                    <div className="absolute right-0 top-0 w-96 h-96 opacity-10">
                        <img
                            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M12,18L20.39,21.39C22.97,18.59 22.12,14.28 18.75,12.6C18.76,12.4 18.76,12.2 18.75,12C21.33,10.32 22.17,6.5 19.59,3.69L12,7L4.41,3.69C1.83,6.5 2.67,10.32 5.25,12C5.24,12.2 5.24,12.4 5.25,12.6C1.88,14.28 1.03,18.59 3.61,21.39L12,18Z'/%3E%3C/svg%3E"
                            alt="Solar panel"
                            className="w-full h-full"
                        />
                    </div>
                    <div className="relative z-10">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            실시간 태양광 발전 모니터링
                        </h2>
                        <p className="text-blue-100 text-base md:text-lg mb-8 max-w-2xl">
                            청정 에너지 생산 현황을 실시간으로 확인하고 발전 효율을
                            최적화하세요
                        </p>
                        <div className="flex flex-col sm:flex-row gap-8 sm:gap-16">
                            <div>
                                <p className="text-blue-100 mb-1">현재 발전량</p>
                                <p className="text-4xl md:text-5xl font-bold text-white">
                                    2,847 <span className="text-xl md:text-2xl">kW</span>
                                </p>
                            </div>
                            <div>
                                <p className="text-blue-100 mb-1">발전 효율</p>
                                <p className="text-4xl md:text-5xl font-bold text-white">
                                    94.2<span className="text-xl md:text-2xl">%</span>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Stats */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <StatCard
                        title="현재 발전량"
                        value="2,847"
                        unit="kW"
                        change={5.2}
                        icon={Sun}
                        color="green"
                    />
                    <StatCard
                        title="오늘 누적 발전량"
                        value="68,420"
                        unit="kWh"
                        change={12.8}
                        icon={Battery}
                        color="blue"
                    />
                    <StatCard
                        title="발전 효율"
                        value="94.2"
                        unit="%"
                        change={2.1}
                        icon={Activity}
                        color="purple"
                    />
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Sun className="w-5 h-5 text-yellow-500" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">일조량</span>
                                </div>
                                <span className="font-semibold text-yellow-600 dark:text-yellow-400">850 W/m²</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Thermometer className="w-5 h-5 text-blue-500" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">기온</span>
                                </div>
                                <span className="font-semibold text-blue-600 dark:text-blue-400">24°C</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Cloud className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">구름량</span>
                                </div>
                                <span className="font-semibold text-gray-600 dark:text-gray-300">15%</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-green-500" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">패널 각도</span>
                                </div>
                                <span className="font-semibold text-green-600 dark:text-green-400">35°</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* 시간별 발전량 */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">시간별 발전량</h3>
                        <span className="px-3 py-1 bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400 rounded-full text-sm font-medium">
                            오늘
                        </span>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={hourlyData}>
                            <defs>
                                <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" className="dark:opacity-10" />
                            <XAxis dataKey="time" stroke="#9ca3af" />
                            <YAxis stroke="#9ca3af" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "rgba(255, 255, 255, 0.9)",
                                    borderRadius: "8px",
                                    border: "none",
                                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                }}
                                labelStyle={{ color: "#111827", fontWeight: "bold" }}
                            />
                            <Area
                                type="monotone"
                                dataKey="power"
                                stroke="#10b981"
                                strokeWidth={3}
                                fill="url(#colorPower)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* 발전소 정보 */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">발전소 정보</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">발전소명</span>
                            <span className="font-semibold dark:text-white">경기 김포 태양광 1호기</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">위치</span>
                            <span className="font-semibold dark:text-white">경기도 김포시 월곶면</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">총 설치 용량</span>
                            <span className="font-semibold dark:text-white">3,500 kW</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">가동 시작일</span>
                            <span className="font-semibold dark:text-white">2023년 3월 15일</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-xl">
                            <span className="text-green-700 dark:text-green-400">현재 상태</span>
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="font-semibold text-green-700 dark:text-green-400">정상</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Daily Trend */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            일별 발전량 트렌드 (최근 30일)
                        </h3>
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">일별 발전량</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded"></div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">평균 발전량</span>
                            </div>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={dailyData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" className="dark:opacity-10" />
                            <XAxis dataKey="date" stroke="#9ca3af" fontSize={11} />
                            <YAxis stroke="#9ca3af" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "rgba(255, 255, 255, 0.9)",
                                    borderRadius: "8px",
                                    border: "none",
                                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                }}
                                labelStyle={{ color: "#111827", fontWeight: "bold" }}
                            />
                            <Bar dataKey="actual" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="average" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Floating Action Buttons */}
            <div className="fixed bottom-8 right-8 flex flex-col gap-4">
                <button className="w-14 h-14 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-all">
                    <AlertCircle className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                </button>
                <button className="w-14 h-14 bg-blue-500 rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-all">
                    <Activity className="w-6 h-6 text-white" />
                </button>
                <button className="w-14 h-14 bg-gray-800 dark:bg-gray-700 rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-all">
                    <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                        />
                    </svg>
                </button>
            </div>
        </div>
    );
};

export default Analysis;
