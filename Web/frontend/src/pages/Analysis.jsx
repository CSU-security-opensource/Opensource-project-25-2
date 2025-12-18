import React, { useState, useEffect } from "react";
import KakaoMap from "../KakaoMap"; // 지도 컴포넌트 불러오기 (경로 확인 필요)
import {
    Sun,
    Cloud,
    Thermometer,
    Activity,
    TrendingUp,
    Battery,
    AlertCircle,
    X,
    MapPin
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

// ------------------------------------------------------
const API = "http://localhost:8000";

// ✅ [수정] props로 plantId를 받음 (기본값 1)
const Analysis = ({ plantId = 1 }) => {
    const [currentTime, setCurrentTime] = useState(new Date());

    // UI 상태
    const [isMapOpen, setIsMapOpen] = useState(false);

    // 데이터 상태
    const [weather, setWeather] = useState(null);
    const [irr, setIrr] = useState(null);
    const [plant, setPlant] = useState(null);
    const [realtime, setRealtime] = useState(null);

    // 차트용 데이터 상태 (API에서 받아옴)
    const [hourlyData, setHourlyData] = useState([]);
    const [dailyData, setDailyData] = useState([]);

    // 1. 실시간 발전량 예측 데이터 (오늘)
    useEffect(() => {
        // ✅ [수정] URL에 plantId 변수 적용
        fetch(`${API}/prediction/realtime/${plantId}`)
            .then(res => res.json())
            .then(data => {
                if (data.data && data.data.length > 0) {
                    // 가장 최신 값 (마지막)
                    setRealtime(data.data[data.data.length - 1]);
                }
            })
            .catch(console.error);
    }, [plantId]); // ✅ [수정] plantId가 바뀔 때마다 실행

    // 2. 발전소 정보 조회
    useEffect(() => {
        // ✅ [수정] URL에 plantId 변수 적용
        fetch(`${API}/plants/${plantId}`)
            .then((res) => res.json())
            .then((data) => {
                setPlant(data);
            })
            .catch((err) => console.error("발전소 정보 API 에러:", err));
    }, [plantId]);

    // 3. 실시간 날씨 및 일사량 조회
    useEffect(() => {
        // 초단기실황 날씨
        // ✅ [수정] URL에 plantId 변수 적용
        fetch(`${API}/weather/current/${plantId}`)
            .then((res) => {
                if (!res.ok) throw new Error("Weather API response error");
                return res.json();
            })
            .then((data) => {
                if (data.weather) {
                    setWeather(data.weather);
                }
            })
            .catch((err) => console.error("날씨 API 에러:", err));

        // 실시간 일사량
        // ✅ [수정] URL에 plantId 변수 적용
        fetch(`${API}/solar/realtime/${plantId}`)
            .then((res) => {
                if (!res.ok) throw new Error("Solar API response error");
                return res.json();
            })
            .then((data) => {
                if (data.ghi !== undefined) {
                    setIrr(data.ghi);
                }
            })
            .catch((err) => console.error("일사량 API 에러:", err));
    }, [plantId]);

    // 4. [NEW] 차트 데이터 조회 (시간별/일별 예측)
    useEffect(() => {
        const fetchForecasts = async () => {
            try {
                // (1) 시간별 예측 (오늘 하루)
                // ✅ [수정] URL에 plantId 변수 적용
                const hourlyRes = await fetch(`${API}/prediction/hourly/today/${plantId}`);
                const hourlyJson = await hourlyRes.json();

                if (hourlyJson.data) {
                    const formattedHourly = hourlyJson.data.map((item) => {
                        const dateObj = new Date(item.forecast_time);
                        return {
                            // X축 표시용 (예: 14시)
                            time: `${dateObj.getHours()}시`,
                            // MW -> kW 변환
                            power: Math.round(item.predicted_power * 1000),
                            fullDate: item.forecast_time
                        };
                    });
                    setHourlyData(formattedHourly);
                }

                // (2) 일별 예측 (30일치)
                // ✅ [수정] URL에 plantId 변수 적용
                const dailyRes = await fetch(`${API}/prediction/daily/3days/${plantId}`);
                const dailyJson = await dailyRes.json();

                if (dailyJson.data) {
                    const formattedDaily = dailyJson.data.map((item) => {
                        const dateObj = new Date(item.forecast_date);
                        return {
                            // X축 표시용 (예: 6/21일)
                            date: `${dateObj.getMonth() + 1}/${dateObj.getDate()}일`,
                            // MW -> kW 변환 (x1000) 및 반올림
                            predicted: Math.round(item.total_power * 1000),
                        };
                    });
                    setDailyData(formattedDaily);
                }

            } catch (err) {
                console.error("예측 차트 데이터 로딩 실패:", err);
            }
        };

        fetchForecasts();
    }, [plantId]);

    // 5. 시계 타이머
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // 현재 값 계산 (기본단위 MW)
    const currentPowerMW = realtime ? realtime.predicted_power : 0;
    const cumulativePowerMWh = realtime ? realtime.cumulative_power : 0;

    // StatCard 컴포넌트
    const StatCard = ({ title, value, unit, change, icon: Icon, color = "blue" }) => (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-${color}-50 dark:bg-gray-700`}>
                    <Icon className={`w-6 h-6 text-${color}-500 dark:text-${color}-400`} />
                </div>
                {change && (
                    <span className={`text-sm font-semibold ${change > 0 ? "text-green-500" : "text-red-500"}`}>
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

            {/* 지도 모달 */}
            {isMapOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
                    onClick={() => setIsMapOpen(false)}
                >
                    <div
                        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden relative animate-fade-in-up"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="p-4 border-b flex justify-between items-center bg-gray-50">
                            <h3 className="font-bold text-lg flex items-center gap-2 text-gray-800">
                                <MapPin className="text-blue-500" /> 발전소 위치 상세
                            </h3>
                            <button
                                onClick={() => setIsMapOpen(false)}
                                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>
                        <div className="p-4 h-[400px]">
                            <KakaoMap plantId={plantId} />
                        </div>
                    </div>
                </div>
            )}

            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
                <div className="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-800 dark:to-blue-600 rounded-3xl p-8 relative overflow-hidden shadow-lg">
                    <div className="absolute right-0 top-0 w-96 h-96 opacity-10">
                        {/* SVG 배경 이미지 */}
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
                            청정 에너지 생산 현황을 실시간으로 확인하고 발전 효율을 최적화하세요
                        </p>
                        <div className="flex flex-col sm:flex-row gap-8 sm:gap-16">
                            <div>
                                <p className="text-blue-100 mb-1">현재 발전량</p>
                                <p className="text-4xl md:text-5xl font-bold text-white">
                                    {/* MW -> kW 변환 (x1000) 및 포맷팅 */}
                                    {(currentPowerMW * 1000).toLocaleString()}
                                    <span className="text-xl md:text-2xl ml-1">kW</span>
                                </p>
                            </div>
                            <div>
                                <p className="text-blue-100 mb-1">발전 효율</p>
                                <p className="text-4xl md:text-5xl font-bold text-white">
                                    {/* MW끼리 나눗셈이므로 변환 불필요 */}
                                    {plant && plant.capacity_mw
                                        ? `${((currentPowerMW / plant.capacity_mw) * 100).toFixed(1)}`
                                        : "--"}
                                    <span className="text-xl md:text-2xl ml-1">%</span>
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
                        // [수정] MW -> kW (먼저 1000 곱하고 소수점 처리)
                        value={(currentPowerMW * 1000).toFixed(2)}
                        unit="kW"
                        change={5.2}
                        icon={Sun}
                        color="green"
                    />
                    <StatCard
                        title="오늘 누적 발전량"
                        // [수정] MWh -> kWh
                        value={(cumulativePowerMWh * 1000).toFixed(2)}
                        unit="kWh"
                        change={12.8}
                        icon={Battery}
                        color="blue"
                    />
                    <StatCard
                        title="발전 효율"
                        // [수정] MW 단위 그대로 계산
                        value={plant && plant.capacity_mw
                            ? ((currentPowerMW / plant.capacity_mw) * 100).toFixed(1)
                            : "--"}
                        unit="%"
                        change={2.1}
                        icon={Activity}
                        color="purple"
                    />

                    {/* 날씨 정보 카드 */}
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Sun className="w-5 h-5 text-yellow-500" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">일조량</span>
                                </div>
                                <span className="font-semibold text-yellow-600 dark:text-yellow-400">
                                    {irr !== null ? `${irr} W/m²` : "--"}
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Thermometer className="w-5 h-5 text-blue-500" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">기온</span>
                                </div>
                                <span className="font-semibold text-blue-600 dark:text-blue-400">
                                    {weather?.temperature ?? "-"} ℃
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Cloud className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                                    <span className="text-sm text-gray-600 dark:text-gray-400">구름량</span>
                                </div>
                                <span className="font-semibold text-gray-600 dark:text-gray-300">
                                    {weather?.cloud ?? "-"}%
                                </span>
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

                {/* 1. 시간별 발전량 차트 (API 연동됨) */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">오늘 시간별 예측 (24시간)</h3>
                        <span className="px-3 py-1 bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400 rounded-full text-sm font-medium">
                            Forecast
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
                            <XAxis
                                dataKey="time"
                                stroke="#9ca3af"
                                interval={2} // 데이터가 많으므로 간격을 둠 (예: 3시간마다 표시)
                            />
                            <YAxis stroke="#9ca3af" unit="kW" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "rgba(255, 255, 255, 0.9)",
                                    borderRadius: "8px",
                                    border: "none",
                                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                }}
                                labelStyle={{ color: "#111827", fontWeight: "bold" }}
                                formatter={(value) => [`${value.toLocaleString()} kW`, "예상 발전량"]}
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

                {/* 2. 발전소 정보 상세 */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">발전소 정보</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">발전소명</span>
                            <span className="font-semibold dark:text-white">{plant ? plant.name : "--"}</span>
                        </div>
                        <div
                            className="flex justify-between items-center p-4 bg-blue-50 rounded-xl cursor-pointer hover:bg-blue-100 transition-colors group"
                            onClick={() => setIsMapOpen(true)}
                            title="클릭해서 지도 보기"
                        >
                            <span className="text-gray-600 dark:text-gray-400">위치</span>
                            <span className="text-xs text-blue-500 bg-white px-2 py-0.5 rounded-full border border-blue-200 opacity-0 group-hover:opacity-100 transition-opacity">지도 보기</span>
                            <span className="font-semibold text-blue-700 underline decoration-blue-300 underline-offset-4">{plant ? plant.place : "--"}</span>
                        </div>

                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">총 설치 용량</span>
                            <span className="font-semibold dark:text-white">{plant ? `${plant.capacity_mw} MW` : "--"}</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <span className="text-gray-600 dark:text-gray-400">가동 시작일</span>
                            <span className="font-semibold dark:text-white">{plant ? plant.start_date : "--"}</span>
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

            {/* Daily Trend (API 연동됨 - 30일치) */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        {/* [수정됨] 제목 변경 */}
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            일별 예상 발전량 (향후 30일)
                        </h3>
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">예상 발전량</span>
                            </div>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={dailyData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" className="dark:opacity-10" />
                            <XAxis
                                dataKey="date"
                                stroke="#9ca3af"
                                fontSize={12}
                                interval={2} // [추천] 30개 데이터라 글자가 겹칠 수 있어 간격을 줍니다
                            />
                            <YAxis stroke="#9ca3af" unit="kW" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "rgba(255, 255, 255, 0.9)",
                                    borderRadius: "8px",
                                    border: "none",
                                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                }}
                                labelStyle={{ color: "#111827", fontWeight: "bold" }}
                                formatter={(value) => [`${value.toLocaleString()} kW`, "예상 발전량"]}
                            />
                            <Bar dataKey="predicted" fill="#3b82f6" radius={[4, 4, 0, 0]} name="예상 발전량" />
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