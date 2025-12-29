import React, { useEffect, useState } from "react";
import { Map, MapMarker, useKakaoLoader } from "react-kakao-maps-sdk";

const API = "http://localhost:8000";

// ✅ [수정] plantId를 props로 받습니다. (기본값 1)
function KakaoMap({ plantId = 1 }) {
  const [loading, error] = useKakaoLoader({
    appkey: "556feed4e7ed48f090f6765df97c4107", // 본인의 카카오 앱 키
  });

  const [plant, setPlant] = useState(null);

  // 발전소 정보 API 호출 (plantId가 바뀔 때마다 실행)
  useEffect(() => {
    if (!plantId) return;

    fetch(`${API}/plants/${plantId}`)
      .then((res) => res.json())
      .then((data) => {
        // 위도/경도 데이터가 있는지 확인
        if (data.latitude && data.longitude) {
          setPlant({
            name: data.name,
            // ✅ [안전장치] DB에서 문자열로 넘어올 경우를 대비해 숫자로 변환
            lat: parseFloat(data.latitude),
            lng: parseFloat(data.longitude),
          });
        } else {
          console.warn(`발전소(ID:${plantId})의 위치 정보가 없습니다.`);
        }
      })
      .catch((err) => console.error("발전소 정보 로드 실패:", err));
  }, [plantId]); // 의존성 배열에 plantId 추가

  if (loading) {
    return <div className="flex items-center justify-center h-full text-gray-500">지도 로딩 중...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center h-full text-red-500">지도 로드 실패</div>;
  }

  if (!plant) {
    return <div className="flex items-center justify-center h-full text-gray-500">위치 정보를 불러오는 중...</div>;
  }

  return (
    <Map
      center={{ lat: plant.lat, lng: plant.lng }}
      level={4}
      style={{ width: "100%", height: "100%", borderRadius: "12px" }}
    >
      <MapMarker position={{ lat: plant.lat, lng: plant.lng }}>
        <div style={{ padding: "6px", color: "#000", fontSize: "13px", fontWeight: "bold" }}>
          {plant.name}
        </div>
      </MapMarker>
    </Map>
  );
}


export default KakaoMap;
