-- 移除博查 / Tavily 联网检索（已有 xxgcms 库执行本脚本）
-- sync_db 不会删除行，已部署环境需显式执行本补丁。

DELETE FROM ai_model WHERE capability = 'web_search';
DELETE FROM ai_provider WHERE provider_type = 'search';
DELETE FROM ai_system_setting WHERE config_key = 'default_search_provider';
