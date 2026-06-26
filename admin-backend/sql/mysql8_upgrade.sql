-- MySQL 8.0 兼容补充脚本（可选）
-- 主要升级逻辑由 manage.py upgrade_mysql8 执行；本文件供手工运维参考。

/*!40101 SET NAMES utf8mb4 */;
/*!40101 SET @OLD_SQL_MODE=@@SESSION.sql_mode */;
SET SESSION sql_mode = REPLACE(REPLACE(@@SESSION.sql_mode, 'NO_ZERO_DATE', ''), 'NO_ZERO_IN_DATE', '');

-- article / article_kw / cate 零日期修复（表存在时执行）
UPDATE `article` SET `add_time` = '1970-01-01 00:00:00' WHERE `add_time` = '0000-00-00 00:00:00';
ALTER TABLE `article` MODIFY COLUMN `add_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP;

UPDATE `article_kw` SET `add_time` = '1970-01-01 00:00:00' WHERE `add_time` = '0000-00-00 00:00:00';
ALTER TABLE `article_kw` MODIFY COLUMN `add_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP;

UPDATE `cate` SET `add_time` = NULL WHERE `add_time` = '0000-00-00 00:00:00';
ALTER TABLE `cate` MODIFY COLUMN `add_time` datetime DEFAULT NULL;

SET SESSION sql_mode = @OLD_SQL_MODE;
