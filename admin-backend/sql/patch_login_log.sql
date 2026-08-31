-- 登录日志表（已有 xxgcms 库执行本脚本，或运行 sync_db --xxgcms）
CREATE TABLE IF NOT EXISTS `login_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(64) NOT NULL DEFAULT '' COMMENT '登录账号',
  `action` varchar(32) NOT NULL COMMENT 'login_success/login_fail/logout',
  `ip` varchar(64) DEFAULT NULL,
  `user_agent` varchar(512) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL COMMENT '失败原因等',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `login_log_user_name_IDX` (`user_name`),
  KEY `login_log_action_IDX` (`action`),
  KEY `login_log_create_time_IDX` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理后台登录日志';
