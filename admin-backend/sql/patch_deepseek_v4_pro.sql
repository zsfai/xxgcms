-- 将 DeepSeek 默认模型更新为 deepseek-v4-pro
UPDATE ai_model m
JOIN ai_provider p ON m.provider_id = p.id
SET m.model_id = 'deepseek-v4-pro', m.display_name = 'DeepSeek V4 Pro'
WHERE p.code = 'deepseek' AND m.is_default = 'Y';
