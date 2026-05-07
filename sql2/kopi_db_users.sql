-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: kopi_db
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

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
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','pelanggan') DEFAULT 'pelanggan',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin Kopi','admin@kopi.com','scrypt:32768:8:1$L4aK6SqlApBCbTgW$4213b838ffba4aedeef1ced49d64cdce01059fd4e2811943006633c036371190468a5a6abcccdf6228985c5e580cc918c549503505f3ee558e8f9dd5617193c4','admin','2026-05-06 16:20:36'),(2,'Budi Santoso','budi@gmail.com','scrypt:32768:8:1$nxZwt7QETUI1Kenv$7ffb69e92acafa609a01f785f7cdb51dfe18cf049d41faa0fb8e344249ef9c40ce7bc15804d661364b683f3a02a824a9c3d6ccd65f6e61185dbb79d17f8fc8ec','pelanggan','2026-05-06 16:20:36'),(3,'Siti Rahayu','siti@gmail.com','scrypt:32768:8:1$q9x7milCdl3g2e6m$1d92f335b65d3c36667c8cb026970f086963b673c2cc5a2cff1baba6b2128724a95dd8dd0ac649c2d001cd8c96c3e51ee622d6ef9f546bae6b1998fe1733c238','pelanggan','2026-05-06 16:20:36'),(4,'kelvin','kelvin@gmail.com','scrypt:32768:8:1$F0ELfBcoGXV6RUEE$66eb5e1a1bddf5e10e88c62e1499f9b536dfa9187a8390446a16299729f796e606287835f2334f16bb57b8f9455920666d79b8917d7e10dc3ecebaa7a3b6e6cc','pelanggan','2026-05-07 08:10:16');
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

-- Dump completed on 2026-05-07 16:01:02
