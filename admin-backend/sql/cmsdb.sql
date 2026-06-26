-- MySQL dump for xxgcms CMS schema (MySQL 8.0+)
--
-- Host: localhost    Database: xxgai
-- ------------------------------------------------------
-- Server version	8.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `add_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cate_id` int(11) DEFAULT '-1',
  `author_id` int(11) DEFAULT NULL,
  `del_flag` char(1) NOT NULL DEFAULT 'N' COMMENT 'Y:已删除，N:未删除',
  `pub_status` char(1) NOT NULL DEFAULT 'N' COMMENT 'Y:已发布，N:未发布',
  `view_num` int(11) DEFAULT '0',
  `source_id` bigint(20) NOT NULL COMMENT '源文章id',
  `kw_matched` char(1) DEFAULT 'N' COMMENT '是否已经匹配了关键词，Y：已匹配，N：未匹配',
  `pub_time` datetime DEFAULT NULL,
  `source_cate_name` varchar(40) DEFAULT NULL COMMENT '源文章分类名称',
  `update_time` datetime DEFAULT NULL,
  `show_type` tinyint(4) NOT NULL DEFAULT '1' COMMENT '文章展示类型，1：图文或纯文字，2：图片集；默认图文',
  `ai_generated` char(1) NOT NULL DEFAULT 'N' COMMENT 'Y:AI生成或辅助',
  `ai_job_id` bigint(20) DEFAULT NULL COMMENT 'AI批量任务id',
  PRIMARY KEY (`id`),
  KEY `article_title_IDX` (`title`(191)) USING BTREE,
  KEY `article_source_id_IDX` (`source_id`) USING BTREE,
  KEY `article_cate_id_IDX` (`cate_id`) USING BTREE,
  KEY `article_pub_time_IDX` (`pub_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article`
--

LOCK TABLES `article` WRITE;
/*!40000 ALTER TABLE `article` DISABLE KEYS */;
INSERT INTO `article` VALUES (1,'hello world!','2020-01-01 00:00:00',-1,NULL,'N','N',0,10000,'N',NULL,NULL,NULL,1,'N',NULL);
/*!40000 ALTER TABLE `article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article_annex`
--

DROP TABLE IF EXISTS `article_annex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_annex` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` longtext NOT NULL,
  `desc` varchar(500) DEFAULT NULL,
  `pic_url` varchar(500) DEFAULT NULL,
  `pic_url2` varchar(500) DEFAULT NULL,
  `pic_url3` varchar(500) DEFAULT NULL,
  `pic_url4` varchar(500) DEFAULT NULL,
  `article_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `article_annex_UN` (`article_id`),
  KEY `article_annex_article_id_IDX` (`article_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article_annex`
--

LOCK TABLES `article_annex` WRITE;
/*!40000 ALTER TABLE `article_annex` DISABLE KEYS */;
/*!40000 ALTER TABLE `article_annex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article_ci`
--

DROP TABLE IF EXISTS `article_ci`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_ci` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(20) DEFAULT NULL,
  `ci_list` varchar(500) DEFAULT NULL COMMENT '文章分词分出来的词组，约定不超过20个，使用英文 , 隔开',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article_ci`
--

LOCK TABLES `article_ci` WRITE;
/*!40000 ALTER TABLE `article_ci` DISABLE KEYS */;
/*!40000 ALTER TABLE `article_ci` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article_kw`
--

DROP TABLE IF EXISTS `article_kw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_kw` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(20) NOT NULL,
  `add_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `kw` varchar(50) DEFAULT NULL,
  `sort` tinyint(4) NOT NULL DEFAULT '99' COMMENT '关键词排序',
  `type` varchar(2) DEFAULT NULL COMMENT '关键词类型：t:来自标题，c：来自内容，r:相关联',
  PRIMARY KEY (`id`),
  KEY `article_kw_article_id_IDX` (`article_id`) USING BTREE,
  KEY `article_kw_kw_IDX` (`kw`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article_kw`
--

LOCK TABLES `article_kw` WRITE;
/*!40000 ALTER TABLE `article_kw` DISABLE KEYS */;
/*!40000 ALTER TABLE `article_kw` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article_slug`
--

DROP TABLE IF EXISTS `article_slug`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_slug` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(20) NOT NULL,
  `slug_url` varchar(70) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章英文链接';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article_slug`
--

LOCK TABLES `article_slug` WRITE;
/*!40000 ALTER TABLE `article_slug` DISABLE KEYS */;
/*!40000 ALTER TABLE `article_slug` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article_source_url`
--

DROP TABLE IF EXISTS `article_source_url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_source_url` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(20) NOT NULL COMMENT '对应文章id',
  `url` varchar(500) DEFAULT NULL COMMENT '采集源文章链接',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章采集的源链接，用于版权或删除文章使用';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article_source_url`
--

LOCK TABLES `article_source_url` WRITE;
/*!40000 ALTER TABLE `article_source_url` DISABLE KEYS */;
/*!40000 ALTER TABLE `article_source_url` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carousel`
--

DROP TABLE IF EXISTS `carousel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `carousel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) DEFAULT NULL,
  `pic_url` varchar(100) DEFAULT NULL,
  `click_url` varchar(200) DEFAULT NULL,
  `sort_num` tinyint(4) DEFAULT '99' COMMENT '排序，数字小靠前',
  `status` varchar(1) DEFAULT '0' COMMENT '生效状态：0：失效，1：有效',
  `create_time` datetime DEFAULT NULL,
  `desc` varchar(100) DEFAULT NULL,
  `del_flag` varchar(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除',
  `click_num` int(11) DEFAULT '0' COMMENT '点击次数',
  `use_for` varchar(10) NOT NULL DEFAULT '' COMMENT 'SXY:省小友，MRB:木容白，BOYP:北欧优品',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carousel`
--

LOCK TABLES `carousel` WRITE;
/*!40000 ALTER TABLE `carousel` DISABLE KEYS */;
/*!40000 ALTER TABLE `carousel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cate`
--

DROP TABLE IF EXISTS `cate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `name_en` varchar(40) DEFAULT NULL COMMENT '英文名称',
  `pic_url` varchar(300) DEFAULT NULL,
  `p_id` int(11) DEFAULT NULL COMMENT '父id',
  `visiable` char(1) DEFAULT 'Y' COMMENT '主菜单栏目是否可见，Y:可见，N:不可见',
  `sort_num` int(11) DEFAULT '999999',
  `kws` varchar(100) DEFAULT '',
  `desc` varchar(200) DEFAULT '',
  `add_time` datetime DEFAULT NULL,
  `del_flag` char(1) NOT NULL DEFAULT 'N' COMMENT 'Y:已删除,N:未删除',
  `update_time` datetime DEFAULT NULL,
  `home_visiable` char(1) DEFAULT NULL COMMENT '首页获取时是否展示该栏目可见',
  `seo_title` varchar(100) NOT NULL DEFAULT '' COMMENT 'seo标题',
  `content` longtext COMMENT '栏目内容',
  PRIMARY KEY (`id`),
  UNIQUE KEY `cate_UN` (`name_en`),
  KEY `NewTable_name_IDX` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cate`
--

LOCK TABLES `cate` WRITE;
/*!40000 ALTER TABLE `cate` DISABLE KEYS */;
/*!40000 ALTER TABLE `cate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ci_invalid`
--

DROP TABLE IF EXISTS `ci_invalid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ci_invalid` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ci` varchar(30) DEFAULT NULL,
  `status` char(1) DEFAULT NULL COMMENT '0:无效,1:生效',
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ci_invalid`
--

LOCK TABLES `ci_invalid` WRITE;
/*!40000 ALTER TABLE `ci_invalid` DISABLE KEYS */;
/*!40000 ALTER TABLE `ci_invalid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ci_map`
--

DROP TABLE IF EXISTS `ci_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ci_map` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ci` varchar(50) DEFAULT NULL COMMENT '原始词',
  `map_ci` varchar(50) DEFAULT NULL COMMENT '映射词',
  `status` varchar(1) NOT NULL COMMENT '0:无效，1:有效',
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ci_map`
--

LOCK TABLES `ci_map` WRITE;
/*!40000 ALTER TABLE `ci_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `ci_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `friend_link`
--

DROP TABLE IF EXISTS `friend_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `friend_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `pic_url` varchar(100) DEFAULT NULL,
  `click_url` varchar(200) DEFAULT NULL,
  `sort_num` tinyint(4) DEFAULT '99' COMMENT '排序，数字小靠前',
  `status` varchar(1) DEFAULT '0' COMMENT '生效状态：0：失效，1：有效',
  `add_time` datetime DEFAULT NULL,
  `desc` varchar(100) DEFAULT NULL,
  `del_flag` varchar(1) NOT NULL DEFAULT '0' COMMENT '逻辑删除',
  `click_num` int(11) DEFAULT '0' COMMENT '点击次数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `friend_link`
--

LOCK TABLES `friend_link` WRITE;
/*!40000 ALTER TABLE `friend_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `friend_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keyword`
--

DROP TABLE IF EXISTS `keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `keyword` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `kw` varchar(100) NOT NULL COMMENT '关键词',
  `del_flag` char(1) NOT NULL DEFAULT 'N' COMMENT '''Y'':已删除,''N'':未删除',
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `kw_slug` varchar(100) DEFAULT NULL COMMENT '关键词中间加横杠，并且都转换成小写',
  PRIMARY KEY (`id`),
  UNIQUE KEY `NewTable_UN` (`kw`),
  UNIQUE KEY `keyword_UN` (`kw`),
  KEY `kw_kw_IDX` (`kw`) USING BTREE,
  KEY `keyword_kw_IDX` (`kw`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keyword`
--

LOCK TABLES `keyword` WRITE;
/*!40000 ALTER TABLE `keyword` DISABLE KEYS */;
/*!40000 ALTER TABLE `keyword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kw_kw`
--

DROP TABLE IF EXISTS `kw_kw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `kw_kw` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source_kw_id` bigint(20) DEFAULT NULL,
  `source_kw` varchar(50) DEFAULT NULL,
  `related_kw_id` bigint(20) DEFAULT NULL,
  `related_kw` varchar(50) DEFAULT NULL,
  `related_kw_sort` tinyint(4) DEFAULT '99',
  PRIMARY KEY (`id`),
  KEY `kw_kw_source_kw_id_IDX` (`source_kw_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kw_kw`
--

LOCK TABLES `kw_kw` WRITE;
/*!40000 ALTER TABLE `kw_kw` DISABLE KEYS */;
/*!40000 ALTER TABLE `kw_kw` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_conf`
--

DROP TABLE IF EXISTS `site_conf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_conf` (
  `site_name` varchar(40) NOT NULL COMMENT '站点名称',
  `title` varchar(64) DEFAULT NULL COMMENT '站点标题',
  `kws` varchar(100) DEFAULT NULL COMMENT '关键词',
  `desc` varchar(200) DEFAULT NULL COMMENT '站点描述',
  `logo_url` varchar(300) DEFAULT NULL COMMENT '站点logo',
  `add_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `defaul_pic_url` varchar(300) DEFAULT NULL COMMENT '默认图片',
  `domain` varchar(50) NOT NULL COMMENT '域名，唯一',
  `favicon_url` varchar(300) DEFAULT NULL COMMENT 'favicon',
  `icp` varchar(100) DEFAULT NULL COMMENT 'icp备案号',
  `theme_dir` varchar(50) DEFAULT 'default' COMMENT '站点模板所在目录',
  `tongji_code` longtext COMMENT '统计代码',
  `https` char(1) DEFAULT 'Y',
  `baidu_tsapi` varchar(256) DEFAULT NULL COMMENT '百度推送api接口',
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点参数配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_conf`
--

LOCK TABLES `site_conf` WRITE;
/*!40000 ALTER TABLE `site_conf` DISABLE KEYS */;
/*!40000 ALTER TABLE `site_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_ret`
--

DROP TABLE IF EXISTS `ts_ret`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ts_ret` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(512) DEFAULT NULL COMMENT '网站需要提交的链接',
  `ts_time` datetime DEFAULT NULL COMMENT '推送的时间',
  `ts_type` varchar(10) DEFAULT '' COMMENT 'baidu:百度，sm:神马，sogo:搜狗，360：360',
  `success` tinyint(2) DEFAULT NULL COMMENT '1:成功,0：失败',
  `msg` varchar(500) DEFAULT NULL COMMENT '失败原因',
  `source_id` bigint(20) DEFAULT NULL COMMENT '文章id',
  PRIMARY KEY (`id`),
  KEY `ts_ret_source_id_IDX` (`source_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='搜索引擎推送提交结果';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_ret`
--

LOCK TABLES `ts_ret` WRITE;
/*!40000 ALTER TABLE `ts_ret` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_ret` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-20 23:12:20
