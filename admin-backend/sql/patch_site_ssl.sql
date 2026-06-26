-- 站点 SSL / 域名别名字段（已有 xxgcms 库执行本脚本，或运行 sync_db --xxgcms）
ALTER TABLE `site` ADD COLUMN `domain_aliases` varchar(500) DEFAULT NULL COMMENT '逗号分隔别名，如 www.example.com';
ALTER TABLE `site` ADD COLUMN `ssl_enabled` char(1) DEFAULT 'N' COMMENT 'Y/N';
ALTER TABLE `site` ADD COLUMN `force_https` char(1) DEFAULT 'Y' COMMENT 'HTTP 301 到 HTTPS';
ALTER TABLE `site` ADD COLUMN `cert_status` varchar(20) DEFAULT 'none' COMMENT 'none/pending/active/expired/error';
ALTER TABLE `site` ADD COLUMN `cert_not_after` datetime DEFAULT NULL;
ALTER TABLE `site` ADD COLUMN `nginx_status` varchar(20) DEFAULT 'none' COMMENT 'none/pending/synced/error';
ALTER TABLE `site` ADD COLUMN `nginx_error` varchar(500) DEFAULT NULL;
