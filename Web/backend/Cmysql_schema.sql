-- ===============================
-- PLANT (발전소 정보)
-- ===============================
DROP TABLE IF EXISTS `PLANT`;
CREATE TABLE `PLANT` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) DEFAULT NULL COMMENT '발전소명',
  `place` VARCHAR(255) DEFAULT NULL COMMENT '위치명 (지번, 행정주소 등)',
  `capacity_mw` FLOAT DEFAULT NULL COMMENT '설치용량(MW)',
  `start_date` DATE DEFAULT NULL COMMENT '가동 시작일',
  `latitude` DECIMAL(9,6) DEFAULT NULL COMMENT '위도',
  `longitude` DECIMAL(9,6) DEFAULT NULL COMMENT '경도',
  PRIMARY KEY (`id`),
  KEY `ix_PLANT_id` (`id`),
  KEY `ix_PLANT_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ===============================
-- WEATHER (기상 정보)
-- ===============================
DROP TABLE IF EXISTS `WEATHER`;
CREATE TABLE `WEATHER` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `plant_id` INT DEFAULT NULL COMMENT '발전소 ID (FK)',
  `timestamp` DATETIME DEFAULT NULL COMMENT '관측 시각',
  `temperature` FLOAT DEFAULT NULL COMMENT '기온 (℃)',
  `insolation` FLOAT DEFAULT NULL COMMENT '일사량 (W/m² 또는 kWh/m²/day)',
  `humidity` FLOAT DEFAULT NULL COMMENT '습도 (%)',
  `cloud_cover` FLOAT DEFAULT NULL COMMENT '구름량 (%)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `_plant_timestamp_uc` (`plant_id`, `timestamp`),
  KEY `ix_WEATHER_id` (`id`),
  KEY `ix_WEATHER_timestamp` (`timestamp`),
  CONSTRAINT `WEATHER_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `PLANT` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ===============================
-- GENERATION (실제 발전량)
-- ===============================
DROP TABLE IF EXISTS `GENERATION`;
CREATE TABLE `GENERATION` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `plant_id` INT DEFAULT NULL,
  `timestamp` DATETIME DEFAULT NULL,
  `actual_power_mwh` FLOAT DEFAULT NULL COMMENT '실제 발전량 (MWh)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `_gen_plant_timestamp_uc` (`plant_id`, `timestamp`),
  KEY `ix_GENERATION_id` (`id`),
  KEY `ix_GENERATION_timestamp` (`timestamp`),
  CONSTRAINT `GENERATION_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `PLANT` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ===============================
-- FORECAST (시간별 발전 예측)
-- ===============================
DROP TABLE IF EXISTS `FORECAST`;
CREATE TABLE `FORECAST` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `plant_id` INT DEFAULT NULL,
  `timestamp` DATETIME DEFAULT NULL,
  `predicted_power_mwh` FLOAT DEFAULT NULL COMMENT '예측 발전량 (MWh)',
  `model_version` VARCHAR(50) DEFAULT NULL COMMENT '모델 버전',
  PRIMARY KEY (`id`),
  UNIQUE KEY `_fc_plant_ts_ver_uc` (`plant_id`, `timestamp`, `model_version`),
  KEY `ix_FORECAST_id` (`id`),
  KEY `ix_FORECAST_timestamp` (`timestamp`),
  CONSTRAINT `FORECAST_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `PLANT` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ===============================
-- DAILY_FORECAST (일별 발전 예측 합계)
-- ===============================
DROP TABLE IF EXISTS `DAILY_FORECAST`;
CREATE TABLE `DAILY_FORECAST` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `plant_id` INT DEFAULT NULL,
  `date` DATE DEFAULT NULL,
  `total_predicted_power_mwh` FLOAT DEFAULT NULL COMMENT '하루 총 예측 발전량 (MWh)',
  `model_version` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `_dfc_plant_date_ver_uc` (`plant_id`, `date`, `model_version`),
  KEY `ix_DAILY_FORECAST_date` (`date`),
  KEY `ix_DAILY_FORECAST_id` (`id`),
  CONSTRAINT `DAILY_FORECAST_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `PLANT` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
