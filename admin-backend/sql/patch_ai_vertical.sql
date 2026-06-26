-- 垂类管理表（已有库执行本脚本，或运行 sync_db）
CREATE TABLE IF NOT EXISTS `ai_vertical` (
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

INSERT IGNORE INTO `ai_vertical` (
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
