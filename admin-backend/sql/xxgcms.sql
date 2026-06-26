-- MySQL dump for xxgcms system schema (MySQL 8.0+)
--
-- Host: localhost    Database: xxgcms
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
-- Table structure for table `site`
--

DROP TABLE IF EXISTS `site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `root_path` varchar(100) DEFAULT NULL COMMENT '站点生成页面或上传文件所在根目录地址',
  `pic_url` varchar(300) DEFAULT NULL,
  `db_host` varchar(50) DEFAULT NULL COMMENT '源站点数据库地址',
  `db_port` varchar(10) DEFAULT NULL,
  `db_name` varchar(40) DEFAULT NULL,
  `db_user` varchar(50) DEFAULT NULL,
  `db_pwd` varchar(64) DEFAULT NULL,
  `db_x_host` varchar(50) DEFAULT NULL COMMENT '系统加工数据使用的数据库，即源站点数据导入的数据库',
  `db_x_port` varchar(10) DEFAULT NULL,
  `db_x_name` varchar(40) DEFAULT NULL,
  `db_x_user` varchar(50) DEFAULT NULL,
  `db_x_pwd` varchar(64) DEFAULT NULL,
  `sort_num` smallint(4) DEFAULT '9999',
  `add_time` datetime DEFAULT NULL,
  `del_flag` char(1) DEFAULT 'N' COMMENT '删除标识,N:未删除，Y:已删除',
  `desc` varchar(200) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `domain_aliases` varchar(500) DEFAULT NULL COMMENT '逗号分隔别名，如 www.example.com',
  `ssl_enabled` char(1) DEFAULT 'N' COMMENT 'Y/N',
  `force_https` char(1) DEFAULT 'Y' COMMENT 'HTTP 301 到 HTTPS',
  `cert_status` varchar(20) DEFAULT 'none' COMMENT 'none/pending/active/expired/error',
  `cert_not_after` datetime DEFAULT NULL,
  `nginx_status` varchar(20) DEFAULT 'none' COMMENT 'none/pending/synced/error',
  `nginx_error` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `site_UN` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site`
--

LOCK TABLES `site` WRITE;
/*!40000 ALTER TABLE `site` DISABLE KEYS */;
/*!40000 ALTER TABLE `site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_user`
--

DROP TABLE IF EXISTS `site_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  `del_flag` char(1) DEFAULT 'N' COMMENT '是否删除，Y:删除，N:未删除',
  `status` tinyint(4) DEFAULT NULL COMMENT '启用状态，暂未使用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点与用户关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_user`
--

LOCK TABLES `site_user` WRITE;
/*!40000 ALTER TABLE `site_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `site_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(20) NOT NULL,
  `user_pwd` varchar(200) NOT NULL,
  `status` tinyint(1) DEFAULT '1' COMMENT '启用状态，暂未使用',
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- AI: provider / model / prompt / topic / batch / log
--

DROP TABLE IF EXISTS `ai_provider`;
CREATE TABLE `ai_provider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL COMMENT 'deepseek/qwen/bocha/tavily',
  `name` varchar(64) NOT NULL,
  `provider_type` varchar(16) NOT NULL COMMENT 'text/image/search',
  `base_url` varchar(256) DEFAULT NULL,
  `api_key_env` varchar(64) DEFAULT NULL COMMENT '环境变量名（备用）',
  `api_key` varchar(512) DEFAULT NULL COMMENT '界面配置的 API Key',
  `enabled` char(1) NOT NULL DEFAULT 'Y',
  `extra_config` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ai_provider_code_UN` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_model`;
CREATE TABLE `ai_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider_id` int(11) NOT NULL,
  `model_id` varchar(64) NOT NULL,
  `display_name` varchar(64) DEFAULT NULL,
  `capability` varchar(16) NOT NULL COMMENT 'text_generation/image_generation/web_search',
  `is_default` char(1) NOT NULL DEFAULT 'N',
  `params` text DEFAULT NULL,
  `enabled` char(1) NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`id`),
  KEY `ai_model_provider_IDX` (`provider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_prompt_template`;
CREATE TABLE `ai_prompt_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL,
  `system_prompt` text,
  `section_schema` text DEFAULT NULL,
  `enabled` char(1) NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ai_prompt_template_code_UN` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_system_setting`;
CREATE TABLE `ai_system_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_key` varchar(64) NOT NULL,
  `config_value` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ai_system_setting_key_UN` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_vertical`;
CREATE TABLE `ai_vertical` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL COMMENT '唯一标识，如 travel',
  `name` varchar(64) NOT NULL COMMENT '展示名称',
  `description` varchar(500) DEFAULT NULL,
  `topic_system_prompt` text NOT NULL COMMENT '选题 system 提示',
  `topic_user_hint` text DEFAULT NULL COMMENT '选题 user 补充说明',
  `article_system_prompt` text NOT NULL COMMENT '写稿 system 提示',
  `article_user_hint` text DEFAULT NULL COMMENT '写稿 user 补充说明',
  `search_queries` text NOT NULL COMMENT '联网检索词模板 JSON 数组，支持 {seed} {year}',
  `default_template_code` varchar(32) DEFAULT NULL COMMENT '默认文章模板 code',
  `default_word_count` int(11) NOT NULL DEFAULT 800,
  `sort_num` int(11) NOT NULL DEFAULT 9999,
  `enabled` char(1) NOT NULL DEFAULT 'Y',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ai_vertical_code_UN` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_topic_session`;
CREATE TABLE `ai_topic_session` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `site_name` varchar(40) NOT NULL,
  `seed_keyword` varchar(200) NOT NULL,
  `vertical` varchar(32) NOT NULL DEFAULT 'general',
  `cate_id` int(11) DEFAULT NULL,
  `suggest_count` int(11) NOT NULL DEFAULT 10,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `search_provider` varchar(32) DEFAULT NULL,
  `text_model` varchar(64) DEFAULT NULL,
  `search_degraded` char(1) NOT NULL DEFAULT 'N',
  `created_by` varchar(40) DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ai_topic_session_site_IDX` (`site_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_topic_suggestion`;
CREATE TABLE `ai_topic_suggestion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `session_id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `angle` varchar(100) DEFAULT NULL,
  `timeliness` varchar(500) DEFAULT NULL,
  `summary` varchar(1000) DEFAULT NULL,
  `ref_snippets` text DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'suggested',
  `article_id` bigint(20) DEFAULT NULL,
  `sort_num` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ai_topic_suggestion_session_IDX` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_search_log`;
CREATE TABLE `ai_search_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `session_id` bigint(20) NOT NULL,
  `query` varchar(300) NOT NULL,
  `provider` varchar(32) NOT NULL,
  `result_count` int(11) NOT NULL DEFAULT 0,
  `raw_preview` text DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ai_search_log_session_IDX` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_batch_job`;
CREATE TABLE `ai_batch_job` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `site_name` varchar(40) NOT NULL,
  `session_id` bigint(20) DEFAULT NULL,
  `cate_id` int(11) DEFAULT NULL,
  `template_code` varchar(32) DEFAULT NULL,
  `word_count` int(11) DEFAULT 800,
  `image_mode` varchar(16) DEFAULT 'ai',
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `total` int(11) NOT NULL DEFAULT 0,
  `done` int(11) NOT NULL DEFAULT 0,
  `failed` int(11) NOT NULL DEFAULT 0,
  `created_by` varchar(40) DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_batch_item`;
CREATE TABLE `ai_batch_item` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `job_id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `suggestion_id` bigint(20) DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `article_id` bigint(20) DEFAULT NULL,
  `error_message` varchar(500) DEFAULT NULL,
  `log_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ai_batch_item_job_IDX` (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ai_generation_log`;
CREATE TABLE `ai_generation_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `site_name` varchar(40) NOT NULL,
  `article_id` bigint(20) DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `text_provider` varchar(32) DEFAULT NULL,
  `text_model` varchar(64) DEFAULT NULL,
  `image_provider` varchar(32) DEFAULT NULL,
  `image_model` varchar(64) DEFAULT NULL,
  `search_provider` varchar(32) DEFAULT NULL,
  `tokens_input` int(11) DEFAULT 0,
  `tokens_output` int(11) DEFAULT 0,
  `image_count` int(11) DEFAULT 0,
  `status` varchar(20) NOT NULL,
  `error_message` varchar(500) DEFAULT NULL,
  `duration_ms` int(11) DEFAULT 0,
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ai_generation_log_site_IDX` (`site_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

LOCK TABLES `ai_provider` WRITE;
INSERT INTO `ai_provider` (`code`, `name`, `provider_type`, `base_url`, `api_key_env`, `enabled`) VALUES
('deepseek', 'DeepSeek', 'text', 'https://api.deepseek.com', 'DEEPSEEK_API_KEY', 'Y'),
('qwen', '通义万相', 'image', 'https://dashscope.aliyuncs.com/api/v1', 'DASHSCOPE_API_KEY', 'Y'),
('bocha', '博查搜索', 'search', 'https://api.bochaai.com', 'BOCHA_API_KEY', 'Y'),
('tavily', 'Tavily', 'search', 'https://api.tavily.com', 'TAVILY_API_KEY', 'Y');
UNLOCK TABLES;

LOCK TABLES `ai_model` WRITE;
INSERT INTO `ai_model` (`provider_id`, `model_id`, `display_name`, `capability`, `is_default`, `params`) VALUES
(1, 'deepseek-v4-pro', 'DeepSeek V4 Pro', 'text_generation', 'Y', '{"temperature": 0.7, "max_tokens": 4096}'),
(2, 'wan2.7-image-pro', '万相 2.7 Pro', 'image_generation', 'Y', '{"size": "2K"}'),
(3, 'default', '博查默认', 'web_search', 'Y', '{"max_results": 5}'),
(4, 'default', 'Tavily默认', 'web_search', 'N', '{"max_results": 5}');
UNLOCK TABLES;

LOCK TABLES `ai_prompt_template` WRITE;
INSERT INTO `ai_prompt_template` (`code`, `name`, `system_prompt`, `enabled`) VALUES
('news_general', '通用资讯', '你是资深资讯编辑，根据事实撰写客观报道。不得捏造数据。输出纯JSON。', 'Y'),
('industry_analysis', '行业分析', '你是行业分析师，撰写有深度的行业观察。不得捏造数据。输出纯JSON。', 'Y'),
('travel_guide', '旅游攻略', '你是资深旅游内容策划，撰写实用、准确的旅游攻略。不得捏造开放时间票价。输出纯JSON。', 'Y');
UNLOCK TABLES;

LOCK TABLES `ai_vertical` WRITE;
INSERT INTO `ai_vertical` (
  `code`, `name`, `description`, `topic_system_prompt`, `topic_user_hint`,
  `article_system_prompt`, `article_user_hint`, `search_queries`,
  `default_template_code`, `default_word_count`, `sort_num`, `enabled`
) VALUES
(
  'travel', '旅游', '旅游目的地、攻略、门票与出行实用内容',
  '你是资深旅游内容策划编辑，熟悉国内旅游目的地、季节玩法、交通住宿与门票政策。根据联网检索摘要提炼选题建议。不得捏造检索中未出现的事实；不确定的价格、开放时间、政策须标注「待核实」。选题标题适合 SEO，角度清晰、可写性强。输出必须是合法 JSON，不要 markdown 代码块。',
  '优先推荐有检索依据、对读者有决策价值的选题；避免空泛口号式标题。',
  '你是专业旅游攻略作者，擅长撰写实用、可落地的出行指南。结构清晰、信息密度高，含交通、门票、游玩顺序、避坑等可执行建议。不得捏造票价、开放时间、交通管制。时间敏感信息若无法核实须标注待核实。输出纯 JSON，不要 markdown。',
  '正文小节 3-5 个；image_hint 用英文描述场景，便于 AI 配图。',
  '["{seed} 旅游攻略 {year}","{seed} 最新 门票 政策","{seed} 必去 景点 推荐","{seed} 交通 住宿 攻略","{seed} 最佳旅游时间"]',
  'travel_guide', 800, 10, 'Y'
),
(
  'news', '资讯', '行业动态、政策解读与时事资讯',
  '你是资深资讯编辑，擅长从检索结果中提炼有新闻价值、可深度解读的选题。不得捏造事实与数据；不确定的信息标注「待核实」。选题应具备时效性与可读性。输出必须是合法 JSON，不要 markdown 代码块。',
  '关注近半年内有讨论度的议题；标题客观，避免标题党。',
  '你是资深资讯作者，客观准确、逻辑清楚。导语点明核心信息，正文分层展开，避免空话套话。不得捏造数据与引述。输出纯 JSON，不要 markdown。',
  '涉及政策、数据时若检索未证实，正文须写「待核实」或回避具体数字。',
  '["{seed} 最新 动态 {year}","{seed} 行业 新闻","{seed} 政策 解读"]',
  'news_general', 800, 20, 'Y'
),
(
  'general', '通用', '通用主题内容，适合多数站点',
  '你是资深内容策划编辑，能根据种子词与检索摘要提炼多样化选题。不得捏造检索中未出现的事实；不确定信息标注「待核实」。选题互不重复、适合 SEO。输出必须是合法 JSON，不要 markdown 代码块。',
  '兼顾入门指南、常见问题、对比选购等读者常搜需求。',
  '你是资深内容作者，表达清晰、信息有用。根据标题与背景写出完整文章，不得捏造数据。输出纯 JSON，不要 markdown。',
  '正文 3-5 小节；每节配图 hint 用英文描述画面。',
  '["{seed} 介绍","{seed} 攻略 {year}","{seed} 常见问题"]',
  'news_general', 800, 30, 'Y'
);
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-20 22:30:02
