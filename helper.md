-- 安装pg_trgm扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 创建中英文混合文本搜索配置
-- 创建混合语言配置
CREATE TEXT SEARCH CONFIGURATION mixed_language (COPY = pg_catalog.english);

-- 修改混合语言配置，添加pg_trgm映射
ALTER TEXT SEARCH CONFIGURATION mixed_language
ALTER MAPPING FOR hword, hword_part, word
WITH pg_trgm.trgm;

-- 创建中文词典
CREATE TEXT SEARCH DICTIONARY chinese_dict (
TEMPLATE = simple,
DICTIONARY = pg_trgm.trgm_word
);

-- 更新混合语言配置，使用中文词典
ALTER TEXT SEARCH CONFIGURATION mixed_language
ALTER MAPPING FOR hword, hword_part, word
WITH pg_trgm.trgm, chinese_dict;

-- 数据库操作
-- 删除现有数据库
DROP DATABASE IF EXISTS university_information_db;

-- 创建新数据库
CREATE DATABASE university_information_db
ENCODING 'UTF8'
LC_COLLATE ='zh_CN.UTF-8'
LC_CTYPE ='zh_CN.UTF-8';

-- 切换到新数据库
\connect university_information_db

-- 授权用户
GRANT ALL PRIVILEGES ON DATABASE university_information_db TO ke;

-- 创建向量索引
CREATE INDEX ON items USING HNSW (embedding vector_cosine_ops);

-- 授权用户对public模式下所有表和序列的权限
GRANT ALL PRIVILEGES ON DATABASE university_information_db TO ke;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ke;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ke;


___
-- 终止所有连接到数据库的会话
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'university_information_db'
AND pid <> pg_backend_pid();

-- 删除数据库
DROP DATABASE university_information_db;