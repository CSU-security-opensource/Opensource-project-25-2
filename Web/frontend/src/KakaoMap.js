import React, { useEffect, useState } from "react";
import { Map, MapMarker, useKakaoLoader } from "react-kakao-maps-sdk";

function KakaoMap() { 
  const [loading, error] = useKakaoLoader({
    appkey: "556feed4e7ed48f090f6765df97c4107",
    libraries: ["services"],
  });

  const [position, setPosition] = useState(null);

  useEffect(() => {
    if (loading) return;

    if (!window.kakao || !window.kakao.maps) {
      console.error("카카오 SDK 로드 실패");
      return;
    }

    const geocoder = new window.kakao.maps.services.Geocoder();
    const address = "경기도 김포시 월곶면";

    geocoder.addressSearch(address, (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const lat = parseFloat(result[0].y);
        const lng = parseFloat(result[0].x);
        setPosition({ lat, lng });
      } else {
        console.error("주소 변환 실패:", status);
      }
    });
  }, [loading]);

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        지도를 불러오는 중...
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500">지도 로딩 실패</div>;
  }

  if (!position) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        위치를 찾는 중...
      </div>
    );
  }

  return (
    <Map
      center={position}
      level={4}
      style={{ width: "100%", height: "100%", borderRadius: "12px" }}
    >
      <MapMarker position={position}>
        <div style={{ padding: "5px", fontSize: "13px" }}>
          경기 김포 태양광 발전소
        </div>
      </MapMarker>
    </Map>
  );
}

export default KakaoMap;
