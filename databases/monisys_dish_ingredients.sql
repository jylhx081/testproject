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
-- Table structure for table `dish_ingredients`
--

DROP TABLE IF EXISTS `dish_ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dish_ingredients` (
  `dish_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '菜品ID，关联dishes表',
  `ingredient_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '食材ID，关联ingredients表',
  `amount_g` float NOT NULL COMMENT '食材用量(克，液体按1ml≈1g换算)',
  PRIMARY KEY (`dish_id`,`ingredient_id`),
  KEY `ingredient_id` (`ingredient_id`),
  CONSTRAINT `dish_ingredients_ibfk_1` FOREIGN KEY (`dish_id`) REFERENCES `dishes` (`dish_id`),
  CONSTRAINT `dish_ingredients_ibfk_2` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`ingredient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='菜品-食材配方关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dish_ingredients`
--

LOCK TABLES `dish_ingredients` WRITE;
/*!40000 ALTER TABLE `dish_ingredients` DISABLE KEYS */;
INSERT INTO `dish_ingredients` VALUES ('D001001','I001001',250),('D001001','I002001',20),('D001001','I003001',15),('D001001','I003002',5),('D001001','I004001',15),('D001001','I005001',10),('D001001','I005002',10),('D001001','I005003',2),('D001001','I005004',1),('D001001','I006001',2),('D001002','I007001',50),('D001003','I008001',50),('D001003','I009001',5),('D001004','I009002',10),('D001004','I010001',80),('D001004','I011001',20),('D001005','I006002',1.5),('D001005','I008001',60),('D001005','I009001',8),('D001005','I012001',150),('D001006','I005005',5),('D001006','I006002',1),('D001006','I009001',6),('D001006','I012002',200),('D001007','I005005',4),('D001007','I006002',1.2),('D001007','I009001',7),('D001007','I012003',200),('D001008','I005005',3),('D001008','I005006',2),('D001008','I006002',1.5),('D001008','I009001',8),('D001008','I012004',150),('D001008','I013001',8),('D001010','I006002',0.8),('D001010','I008001',80),('D001010','I015001',120);
/*!40000 ALTER TABLE `dish_ingredients` ENABLE KEYS */;
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
