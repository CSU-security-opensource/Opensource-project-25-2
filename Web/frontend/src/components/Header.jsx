import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';

const Header = ({ onNavigate, currentView }) => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const navItems = [
        { id: 'home', label: '홈' },
        { id: 'powerplant', label: '발전소 현황' },
        { id: 'analysis', label: '데이터 분석' },
        { id: 'settings', label: '설정' },
    ];

    const handleNavClick = (view) => {
        onNavigate(view);
        setIsMobileMenuOpen(false);
    };

    return (
        <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 transition-colors duration-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center gap-4 cursor-pointer" onClick={() => handleNavClick('home')}>
                        <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-xs">logo</span>
                        </div>
                        <h1 className="text-lg font-bold text-gray-900 dark:text-white hidden sm:block">
                            에너지 모니터링 시스템
                        </h1>
                    </div>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex gap-8 text-sm font-medium">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => handleNavClick(item.id)}
                                className={`transition-colors ${currentView === item.id
                                    ? 'text-green-600 dark:text-green-400 font-bold'
                                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                                    }`}
                            >
                                {item.label}
                            </button>
                        ))}
                    </nav>

                    {/* Mobile Menu Button */}
                    <button
                        className="md:hidden p-2 text-gray-600 dark:text-gray-300"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    >
                        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Nav */}
            {isMobileMenuOpen && (
                <div className="md:hidden bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
                    <div className="px-4 pt-2 pb-4 space-y-1">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => handleNavClick(item.id)}
                                className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium ${currentView === item.id
                                    ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                                    }`}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </header>
    );
};

export default Header;
