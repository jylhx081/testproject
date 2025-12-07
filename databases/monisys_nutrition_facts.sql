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
-- Table structure for table `nutrition_facts`
--

DROP TABLE IF EXISTS `nutrition_facts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nutrition_facts` (
  `ingredient_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '食材ID，关联ingredients表',
  `energy_kcal` float DEFAULT NULL COMMENT '热量(千卡/100g)',
  `protein_g` float DEFAULT NULL COMMENT '蛋白质(克/100g)',
  `fat_g` float DEFAULT NULL COMMENT '脂肪(克/100g)',
  `carbohydrate_g` float DEFAULT NULL COMMENT '碳水化合物(克/100g)',
  `fiber_g` float DEFAULT NULL COMMENT '膳食纤维(克/100g)',
  `sodium_mg` float DEFAULT NULL COMMENT '钠(毫克/100g)',
  `calcium_mg` float DEFAULT NULL COMMENT '钙(毫克/100g)',
  `vitamin_c_mg` float DEFAULT NULL COMMENT '维生素C(毫克/100g)',
  PRIMARY KEY (`ingredient_id`),
  CONSTRAINT `nutrition_facts_ibfk_1` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`ingredient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='食材营养成分表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nutrition_facts`
--

LOCK TABLES `nutrition_facts` WRITE;
/*!40000 ALTER TABLE `nutrition_facts` DISABLE KEYS */;
INSERT INTO `nutrition_facts` VALUES ('I001001',395,13.2,37,0,0,63,6,0),('I002001',397,0,0,99.3,0,2.4,23,0),('I003001',20,3,0.1,1.7,0,6300,15,0),('I003002',19,2.9,0.2,1.5,0,5900,12,0),('I004001',110,0.1,0,2.6,0,45,5,0),('I005001',80,1.3,0.6,17.8,2.7,14.9,27,4),('I005002',30,1.7,0.3,6.5,1.3,4.8,29,17),('I005003',314,3.8,5.6,75.4,4.3,14.7,68,0),('I005004',277,1.7,2.7,71.5,5.3,6.4,88,0),('I005005',128,4.5,0.2,27.6,1.3,19.6,39,7),('I005006',246,15.2,12.7,52.7,41.7,21.4,123,0),('I005007',258,6.7,8.9,66.5,28.7,47,639,0),('I006001',0,0,0,0,0,39311,22,0),('I006002',0,0,0,0,0,39300,20,0),('I007001',345,7.4,0.8,77.9,0.6,2.7,13,0),('I008001',143,12.6,9.9,1.5,0,130,56,0),('I009001',899,0,99.9,0,0,1,13,0),('I009002',895,0,99.2,0,0,3,1,0),('I010001',118,22.6,1.9,0,0,75,12,0),('I011001',358,7.2,1.5,78.6,1.8,1100,21,0),('I012001',18,0.9,0.2,4,0.5,5,10,19),('I012002',20,2.2,0.3,3.6,1.4,94,99,25),('I012003',17,1.5,0.2,3.2,1,70,50,47),('I012004',77,2,0.2,17.2,0.7,2.7,8,27),('I013001',31,2.1,0.3,4.9,0.4,260,18,0),('I013002',180,10.2,12.5,15.6,1.5,6012,53,0),('I014001',60,5.7,3.6,2.6,0.4,7,116,0);
/*!40000 ALTER TABLE `nutrition_facts` ENABLE KEYS */;
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
