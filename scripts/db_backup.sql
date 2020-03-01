USE groceries;
-- MySQL dump 10.13  Distrib 8.0.19, for Linux (x86_64)
--
-- Host: db    Database: groceries
-- ------------------------------------------------------
-- Server version	8.0.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `author_table`
--

DROP TABLE IF EXISTS `author_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `author_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `author_table`
--

LOCK TABLES `author_table` WRITE;
/*!40000 ALTER TABLE `author_table` DISABLE KEYS */;
INSERT INTO `author_table` VALUES (1,'Andy Fortman');
/*!40000 ALTER TABLE `author_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grocery_table`
--

DROP TABLE IF EXISTS `grocery_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grocery_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `brand` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `price` float NOT NULL,
  `ounces` float NOT NULL,
  `quality_id` int NOT NULL,
  `date` datetime NOT NULL,
  `author_id` int NOT NULL,
  `store_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grocery_table`
--

LOCK TABLES `grocery_table` WRITE;
/*!40000 ALTER TABLE `grocery_table` DISABLE KEYS */;
INSERT INTO `grocery_table` VALUES (1,'Test1','Test',1.11,22,3,'2020-02-28 23:36:12',1,1),(2,'Test2','Brand 2',2.25,15,2,'2020-02-28 23:37:04',1,2);
/*!40000 ALTER TABLE `grocery_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quality_table`
--

DROP TABLE IF EXISTS `quality_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quality_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quality_table`
--

LOCK TABLES `quality_table` WRITE;
/*!40000 ALTER TABLE `quality_table` DISABLE KEYS */;
INSERT INTO `quality_table` VALUES (1,'Very High'),(2,'High'),(3,'Medium'),(4,'Low'),(5,'Very Low');
/*!40000 ALTER TABLE `quality_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `store_table`
--

DROP TABLE IF EXISTS `store_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `store_table` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `store_table`
--

LOCK TABLES `store_table` WRITE;
/*!40000 ALTER TABLE `store_table` DISABLE KEYS */;
INSERT INTO `store_table` VALUES (1,'Fake Store'),(2,'Testing Store');
/*!40000 ALTER TABLE `store_table` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-01  6:28:52
