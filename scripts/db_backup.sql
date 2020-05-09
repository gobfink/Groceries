USE groceries;
-- MySQL dump 10.13  Distrib 8.0.17, for Linux (x86_64)
--
-- Host: db    Database: groceries
-- ------------------------------------------------------
-- Server version	8.0.17

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('3420c0e31703');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authorTable`
--

DROP TABLE IF EXISTS `authorTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authorTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authorTable`
--

LOCK TABLES `authorTable` WRITE;
/*!40000 ALTER TABLE `authorTable` DISABLE KEYS */;
INSERT INTO `authorTable` VALUES (0,'Anonymous'),(2,'Andy');
/*!40000 ALTER TABLE `authorTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groceryTable`
--

DROP TABLE IF EXISTS `groceryTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `groceryTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `ounces` float DEFAULT NULL,
  `brand` varchar(80) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `store_id` int(11) DEFAULT NULL,
  `quality_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `quality_id` (`quality_id`),
  KEY `store_id` (`store_id`),
  CONSTRAINT `groceryTable_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `authorTable` (`id`),
  CONSTRAINT `groceryTable_ibfk_2` FOREIGN KEY (`quality_id`) REFERENCES `qualityTable` (`id`),
  CONSTRAINT `groceryTable_ibfk_3` FOREIGN KEY (`store_id`) REFERENCES `storeTable` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groceryTable`
--

LOCK TABLES `groceryTable` WRITE;
/*!40000 ALTER TABLE `groceryTable` DISABLE KEYS */;
INSERT INTO `groceryTable` VALUES (8,'test',1.99,123,'brand','2020-04-11 15:53:14',0,1,3),(9,'other',200,12,'b2','2020-04-11 15:57:10',0,1,1),(10,'bob',99,1.67,'ddd','2020-05-01 16:03:41',0,6,2);
/*!40000 ALTER TABLE `groceryTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qualityTable`
--

DROP TABLE IF EXISTS `qualityTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qualityTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qualityTable`
--

LOCK TABLES `qualityTable` WRITE;
/*!40000 ALTER TABLE `qualityTable` DISABLE KEYS */;
INSERT INTO `qualityTable` VALUES (1,'Terrible'),(2,'Less bad'),(3,'Ok'),(4,'Good'),(5,'Very good');
/*!40000 ALTER TABLE `qualityTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storeTable`
--

DROP TABLE IF EXISTS `storeTable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `storeTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storeTable`
--

LOCK TABLES `storeTable` WRITE;
/*!40000 ALTER TABLE `storeTable` DISABLE KEYS */;
INSERT INTO `storeTable` VALUES (1,'store 1'),(2,'test store 2'),(4,'other test'),(5,'super fake store'),(6,'ALEX\'S STORE!');
/*!40000 ALTER TABLE `storeTable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_AcroTag`
--

DROP TABLE IF EXISTS `tbl_AcroTag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_AcroTag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `acroID` int(11) DEFAULT NULL,
  `tagID` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `acroID` (`acroID`),
  KEY `tagID` (`tagID`),
  CONSTRAINT `tbl_AcroTag_ibfk_1` FOREIGN KEY (`acroID`) REFERENCES `tbl_Acronym` (`id`),
  CONSTRAINT `tbl_AcroTag_ibfk_2` FOREIGN KEY (`tagID`) REFERENCES `tbl_Tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_AcroTag`
--

LOCK TABLES `tbl_AcroTag` WRITE;
/*!40000 ALTER TABLE `tbl_AcroTag` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_AcroTag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_Acronym`
--

DROP TABLE IF EXISTS `tbl_Acronym`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_Acronym` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `acronym` varchar(80) DEFAULT NULL,
  `definition` text,
  `name` varchar(100) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `dateCreate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tbl_Acronym_acronym` (`acronym`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `tbl_Acronym_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `tbl_User` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_Acronym`
--

LOCK TABLES `tbl_Acronym` WRITE;
/*!40000 ALTER TABLE `tbl_Acronym` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_Acronym` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_Tag`
--

DROP TABLE IF EXISTS `tbl_Tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_Tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tbl_Tag_tag` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_Tag`
--

LOCK TABLES `tbl_Tag` WRITE;
/*!40000 ALTER TABLE `tbl_Tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_Tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_User`
--

DROP TABLE IF EXISTS `tbl_User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userEmail` varchar(80) DEFAULT NULL,
  `username` varchar(80) DEFAULT NULL,
  `userFN` varchar(80) DEFAULT NULL,
  `userLN` varchar(80) DEFAULT NULL,
  `userPasswordHash` varchar(128) DEFAULT NULL,
  `userIsAdmin` int(11) DEFAULT NULL,
  `userLastLoginDT` datetime DEFAULT NULL,
  `userLoginDT` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tbl_User_userEmail` (`userEmail`),
  UNIQUE KEY `ix_tbl_User_username` (`username`),
  KEY `ix_tbl_User_userFN` (`userFN`),
  KEY `ix_tbl_User_userLN` (`userLN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_User`
--

LOCK TABLES `tbl_User` WRITE;
/*!40000 ALTER TABLE `tbl_User` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_User` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-05-09 19:42:25
