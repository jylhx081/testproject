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
-- Table structure for table `dishes`
--

DROP TABLE IF EXISTS `dishes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dishes` (
  `dish_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '菜品ID，格式D+6位数字（如D001001）',
  `name` varchar(100) COLLATE utf8mb3_bin NOT NULL COMMENT '菜品名称',
  `canteen_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '所属食堂ID，关联canteens表',
  `cooking_method` varchar(50) COLLATE utf8mb3_bin DEFAULT NULL COMMENT '烹饪方式',
  `description` text COLLATE utf8mb3_bin COMMENT '菜品描述',
  PRIMARY KEY (`dish_id`),
  UNIQUE KEY `name` (`name`),
  KEY `canteen_id` (`canteen_id`),
  CONSTRAINT `dishes_ibfk_1` FOREIGN KEY (`canteen_id`) REFERENCES `canteens` (`canteen_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='菜品基础信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dishes`
--

LOCK TABLES `dishes` WRITE;
/*!40000 ALTER TABLE `dishes` DISABLE KEYS */;
INSERT INTO `dishes` VALUES ('D001001','红烧肉','C001001','炖','经典本帮红烧肉，精选五花肉慢炖，肥而不腻，甜咸适口，色泽红亮'),('D001002','米饭','C001001','蒸','东北五常大米蒸制，口感软糯，颗粒饱满'),('D001003','煎蛋','C001001','煎','农家土鸡蛋煎制，单面微焦，蛋黄溏心，无额外添加盐'),('D001004','脆皮炸鸡','C001001','炸','鸡胸肉裹脆皮粉炸制，外酥里嫩，无额外调味（基础款）'),('D001005','西红柿炒鸡蛋','C001001','炒','时令西红柿搭配土鸡蛋炒制，酸甜适口，食堂经典家常菜'),('D001006','炒空心菜','C001001','炒','新鲜空心菜加蒜末清炒，少油少盐，清爽解腻'),('D001007','炒大白菜','C001001','炒','新鲜大白菜梗叶同炒，加蒜末提香，清淡适口'),('D001008','酸辣土豆丝','C001001','炒','土豆丝加干辣椒、醋炒制，酸辣开胃，脆爽可口'),('D001009','麻婆豆腐','C001001','烧','嫩豆腐加豆瓣酱、花椒粉烧制，麻辣鲜香，微麻微辣（食堂改良版）'),('D001010','鸡蛋羹','C001001','蒸','土鸡蛋加温水蒸制，嫩滑无腥，低盐清淡（适合老人/学生）');
/*!40000 ALTER TABLE `dishes` ENABLE KEYS */;
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
