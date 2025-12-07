-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: monisys
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `health_goal` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '健康目标：减脂、维持、增肌',
  `target_speed` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '目标速度：慢速、中速、快速',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'1','scrypt:32768:8:1$nYywoYeITkUQ7mLh$3aa69a37b6bbb202f6f6c4859091973d61124693e6bf749174d4645e61e97f863abe32c68ae2058222636be89b74cb8c00f6fa0b54072c42ae4d02471a2cf97d','1@qq.com',160,50,20,'女',0,1,'2025-12-03 15:02:16','2025-12-06 18:28:45',NULL,NULL),(2,'admin','scrypt:32768:8:1$v7c5Bp9URFQ0BOOf$32c88726443dde5149711f5e34dad16ab13234a24452f65725a1c54d60787c86a3ca5aa4ac9f276a02d9d394d4e1868d9669779541d6e0d9d7a39099518b949c','2934221302@qq.com',NULL,NULL,NULL,NULL,1,1,'2025-12-03 15:04:16','2025-12-06 17:02:55',NULL,NULL),(3,'2','scrypt:32768:8:1$slHgO0Zxpk3bgMfX$343df55fc64a51c8a37f076e4076b7b8fe887d4b8a8d855bf8c47e22314ff31a4e5423d7c48ad3a516aae356036afb5f9410b98ec929703387281c430e7110b0','2@qq.com',160,56,25,'男',0,1,'2025-12-05 09:42:57','2025-12-05 09:43:05',NULL,NULL),(4,'3','scrypt:32768:8:1$CgKkhZwrHRccld4n$bc4dfe73f53b390693ed49d72ede60d1e300620122b2b9b877f5abcbfd0d0f32f664179a144fe46227de14d4a901182337b02bf16b331e96a719a72279a0e2f5','3@qq.com',160,56,25,NULL,0,1,'2025-12-06 16:22:50','2025-12-06 16:22:57',NULL,NULL),(10,'5','scrypt:32768:8:1$Tci39RxP1gtmlkHc$5896a58c895a16d680f131818ebc6b221faf8f2a59fba40fd0ada97397740349a9008154b1016a97bd06373ff2f435096b9ffbbb1a475f6373eb731c73d36a22','5@qq.com',160,50,20,'男',0,1,'2025-12-06 16:58:52','2025-12-06 16:59:02','减脂','慢速');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-07 14:07:28
