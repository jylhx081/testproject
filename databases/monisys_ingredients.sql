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
-- Table structure for table `ingredients`
--

DROP TABLE IF EXISTS `ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredients` (
  `ingredient_id` varchar(7) COLLATE utf8mb3_bin NOT NULL COMMENT '食材ID，格式I+6位数字（如I001001）',
  `ingredient_name` varchar(100) COLLATE utf8mb3_bin NOT NULL COMMENT '食材名称',
  `unit` varchar(20) COLLATE utf8mb3_bin DEFAULT 'g' COMMENT '食材单位（g/ml/个等）',
  PRIMARY KEY (`ingredient_id`),
  UNIQUE KEY `ingredient_name` (`ingredient_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin COMMENT='食材基础信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredients`
--

LOCK TABLES `ingredients` WRITE;
/*!40000 ALTER TABLE `ingredients` DISABLE KEYS */;
INSERT INTO `ingredients` VALUES ('I001001','五花肉','g'),('I002001','冰糖','g'),('I003001','生抽','ml'),('I003002','老抽','ml'),('I004001','料酒','ml'),('I005001','生姜','g'),('I005002','大葱','g'),('I005003','八角','g'),('I005004','桂皮','g'),('I005005','大蒜','g'),('I005006','干辣椒','g'),('I005007','花椒粉','g'),('I006001','食盐','g'),('I006002','食用盐（细盐）','g'),('I007001','大米','g'),('I008001','鸡蛋（生）','g'),('I009001','大豆油','ml'),('I009002','玉米油','ml'),('I010001','鸡胸肉','g'),('I011001','炸鸡裹粉','g'),('I012001','西红柿','g'),('I012002','空心菜','g'),('I012003','大白菜','g'),('I012004','土豆','g'),('I013001','香醋','ml'),('I013002','郫县豆瓣酱','g'),('I014001','嫩豆腐（南豆腐）','g'),('I015001','温水','ml');
/*!40000 ALTER TABLE `ingredients` ENABLE KEYS */;
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
