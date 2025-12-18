import React from 'react';
import { Activity, Database, Zap, ArrowRight, BarChart2, Server } from 'lucide-react';

const Home = ({ onNavigate }) => {
    return (
        <div className="relative min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center overflow-hidden transition-colors duration-200">

            {/* Abstract Background Elements */}
            <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                {/* Animated Orbs/Gradients */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-400/20 dark:bg-blue-600/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2"></div>
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-green-400/20 dark:bg-green-600/10 rounded-full blur-[120px] translate-y-1/2 -translate-x-1/4"></div>

                {/* Grid Pattern */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 dark:opacity-40"></div>
                <div className="absolute inset-0"
                    style={{
                        backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(148, 163, 184, 0.2) 1px, transparent 0)',
                        backgroundSize: '40px 40px'
                    }}
                ></div>
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-12 md:py-20">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">

                    {/* Text Content */}
                    <div className="space-y-8">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm font-medium text-blue-600 dark:text-blue-400 shadow-sm animate-fade-in-up">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                            </span>
                            Jeju Energy Data System v2.0
                        </div>

                        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-gray-900 dark:text-white leading-[1.1]">
                            Data <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500 dark:from-blue-400 dark:to-cyan-300">Intelligent</span><br />
                            Energy Future.
                        </h1>

                        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-lg leading-relaxed">
                            제주의 태양광 발전 데이터를 실시간으로 분석하고 시각화합니다.
                            <br className="hidden md:block" />
                            효율적인 에너지 관리를 위한 직관적인 인사이트를 경험하세요.
                        </p>

                        <div className="flex flex-wrap gap-4 pt-4">
                            <div className="group relative">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-xl blur opacity-30 group-hover:opacity-100 transition duration-200"></div>
                                <button
                                    onClick={() => onNavigate('analysis')}
                                    className="relative flex items-center gap-2 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-bold text-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-all transform hover:-translate-y-0.5 cursor-pointer"
                                >
                                    대시보드 바로가기
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>
                            <button className="px-8 py-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                                더 알아보기
                            </button>
                        </div>
                    </div>

                    {/* Visual/Abstract Graphic */}
                    <div className="relative hidden lg:block">
                        <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/10 to-purple-500/10 rounded-3xl transform rotate-3 scale-105 blur-xl"></div>
                        <div className="relative bg-white/50 dark:bg-gray-800/50 backdrop-blur-xl border border-gray-200 dark:border-gray-700 rounded-2xl p-8 shadow-2xl">
                            {/* Mock Data Visualization Grid */}
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                                    <Activity className="w-8 h-8 text-blue-500 mb-2" />
                                    <div className="text-2xl font-bold text-gray-900 dark:text-white">98.4%</div>
                                    <div className="text-xs text-gray-500 uppercase tracking-wider">Uptime</div>
                                </div>
                                <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                                    <Zap className="w-8 h-8 text-yellow-500 mb-2" />
                                    <div className="text-2xl font-bold text-gray-900 dark:text-white">4.2 MW</div>
                                    <div className="text-xs text-gray-500 uppercase tracking-wider">Generation</div>
                                </div>
                            </div>

                            {/* Mock Graph */}
                            <div className="bg-white dark:bg-gray-900 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 mb-4 h-32 flex items-end justify-between px-2 pb-2 gap-2">
                                {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
                                    <div key={i} className="w-full bg-blue-100 dark:bg-blue-900/30 rounded-t-sm relative group">
                                        <div
                                            className="absolute bottom-0 left-0 right-0 bg-blue-500 dark:bg-blue-500 rounded-t-sm transition-all duration-1000 ease-out"
                                            style={{ height: `${h}%` }}
                                        ></div>
                                    </div>
                                ))}
                            </div>

                            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg">
                                <div className="flex items-center gap-2">
                                    <Server className="w-4 h-4" />
                                    <span>System Status</span>
                                </div>
                                <span className="text-green-500 font-medium flex items-center gap-1">
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                    Operational
                                </span>
                            </div>
                        </div>

                        {/* Floating Elements */}
                        <div className="absolute -top-8 -right-8 p-4 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 animate-bounce delay-1000">
                            <Database className="w-6 h-6 text-purple-500" />
                        </div>
                        <div className="absolute -bottom-6 -left-6 p-4 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 animate-bounce delay-700">
                            <BarChart2 className="w-6 h-6 text-green-500" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
