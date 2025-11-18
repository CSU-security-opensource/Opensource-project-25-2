# 태양광 발전 모니터링 시스템

제주도의 재생에너지 발전 현황을 실시간으로 모니터링하는 React 애플리케이션입니다.

## 주요 기능

### 1. 대시보드 화면 (`solar-monitoring-dashboard-updated.jsx`)

- 실시간 태양광 발전량 모니터링
- 시간별 발전량 그래프
- 일별 발전량 트렌드
- 발전소 정보 카드
- 현재 기상 정보

### 2. 발전소 현황 화면 (`발전소-updated.jsx`)

- 제주도 전체 발전소 목록
- 발전소 유형별 통계 (태양광, 풍력, 화력, 수력)
- 발전소 검색 및 필터링
- 페이지네이션
- 발전소 위치 지도
- 에너지원별 점유율 차트

## 네비게이션 기능

- **홈 버튼**: 대시보드 화면으로 이동
- **발전소 현황 버튼**: 발전소 현황 화면으로 이동

## 파일 구조

```
frontend/
├── App.jsx                          # 메인 앱 컴포넌트 (라우팅 관리)
├── solar-monitoring-dashboard-updated.jsx  # 대시보드 화면
├── 발전소-updated.jsx                # 발전소 현황 화면
├── index.js                         # React 앱 진입점
├── index.css                        # 기본 스타일
├── package-updated.json             # 의존성 패키지 정보
└── public/
    └── index.html                   # HTML 템플릿
```

## 설치 및 실행

1. 의존성 패키지 설치:

```bash
npm install
```

2. 개발 서버 시작:

```bash
npm start
```

3. 브라우저에서 `http://localhost:3000` 접속

## 사용된 기술

- **React 18**: UI 프레임워크
- **Lucide React**: 아이콘 라이브러리
- **Recharts**: 차트 라이브러리
- **Tailwind CSS**: CSS 프레임워크 (CDN 방식)

## 데이터 연동

현재는 Mock 데이터를 사용하고 있습니다. 실제 제주도 발전량 데이터와 연동하려면:

1. EDA 노트북에서 생성한 `jeju_renewable_energy.csv` 파일을 백엔드 API로 제공
2. 각 컴포넌트의 데이터 부분을 API 호출로 대체
3. 실시간 데이터 업데이트를 위한 WebSocket 연결 구현

## 향후 개선 사항

- 실제 데이터베이스 연동
- 실시간 데이터 스트리밍
- 지도 컴포넌트 구현
- 반응형 모바일 최적화
- 다크 테마 지원
