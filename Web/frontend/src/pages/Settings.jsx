import React from 'react';
import { Settings as SettingsIcon, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const Settings = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 transition-colors duration-200">
      <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 transition-colors duration-200">
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-xl transition-colors duration-200">
            <SettingsIcon className="w-8 h-8 text-gray-600 dark:text-gray-300" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">설정</h2>
        </div>

        <div className="space-y-6">
          <div className="border-b border-gray-100 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">계정 설정</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">계정 정보 및 보안 설정을 관리합니다.</p>
            <button className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              프로필 수정
            </button>
          </div>

          <div className="border-b border-gray-100 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">알림 설정</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">이메일 및 푸시 알림 수신 여부를 설정합니다.</p>
            <div className="flex items-center gap-3">
              <input type="checkbox" id="email-notif" className="w-4 h-4 text-green-600 rounded bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600" defaultChecked />
              <label htmlFor="email-notif" className="text-gray-700 dark:text-gray-300">이메일 알림 받기</label>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">시스템 설정</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">다크 모드, 언어 등 시스템 환경을 설정합니다.</p>
            <div className="flex items-center gap-4">
              <button
                onClick={toggleTheme}
                className="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                {theme === 'light' ? (
                  <>
                    <Moon className="w-4 h-4" />
                    다크 모드로 전환
                  </>
                ) : (
                  <>
                    <Sun className="w-4 h-4" />
                    라이트 모드로 전환
                  </>
                )}
              </button>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                현재: {theme === 'light' ? '라이트 모드' : '다크 모드'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
