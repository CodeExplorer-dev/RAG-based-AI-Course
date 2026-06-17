-- ============================================================
-- 基于RAG技术的AI课程答疑与知识点图谱系统
-- 数据库初始化脚本
-- 版本: 1.0 | 引擎: InnoDB | 字符集: utf8mb4
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS rag_course_ai
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE rag_course_ai;

-- ============================================================
-- 1. 用户表 (users)
-- 存储系统用户信息：学生、教师、管理员
-- ============================================================
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL,
    password        VARCHAR(255) NOT NULL,
    email           VARCHAR(100) NULL,
    role            ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE INDEX idx_username (username),
    UNIQUE INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- ============================================================
-- 2. 课程表 (courses)
-- 存储课程基本信息
-- ============================================================
CREATE TABLE courses (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    course_name            VARCHAR(200) NOT NULL,
    description     TEXT         NULL COMMENT '课程简介',
    teacher_id      INT          NOT NULL COMMENT '授课教师ID',
    join_code       VARCHAR(20)  NOT NULL UNIQUE COMMENT '选课码',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_teacher (teacher_id),

    CONSTRAINT fk_courses_teacher
        FOREIGN KEY (teacher_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';


-- ============================================================
-- 3. 用户-课程关联表 (user_courses)
-- 多对多关系：学生选课 / 教师授课
-- ============================================================
CREATE TABLE user_courses (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT      NOT NULL,
    course_id       INT      NOT NULL,
    role            ENUM('student', 'teacher') NOT NULL DEFAULT 'student' COMMENT '用户在课程中的角色',
    enrolled_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE INDEX idx_user_course_role (user_id, course_id, role),
    INDEX idx_course (course_id),

    CONSTRAINT fk_uc_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uc_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户-课程关联表';


-- ============================================================
-- 4. 课件表 (courseware)
-- 存储上传的课件文档元信息（PDF/PPT/DOCX等）
-- ============================================================
CREATE TABLE courseware (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    course_id       INT          NOT NULL,
    title           VARCHAR(300) NOT NULL COMMENT '课件标题',
    file_type       ENUM('pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'md') NOT NULL,
    file_path       VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size       BIGINT       NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
    page_count      INT          NULL     COMMENT '页数/段落数',
    uploader_id     INT          NOT NULL COMMENT '上传者ID',
    chunk_count     INT          NOT NULL DEFAULT 0 COMMENT '已分块数量',
    status          ENUM('uploading', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'uploading',
    uploaded_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_course (course_id),
    INDEX idx_uploader (uploader_id),
    INDEX idx_status (status),

    CONSTRAINT fk_cw_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cw_uploader
        FOREIGN KEY (uploader_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课件表';


-- ============================================================
-- 5. 文档分块表 (document_chunks)
-- 存储课件文档的分块内容，用于RAG语义检索
-- ============================================================
CREATE TABLE document_chunks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    courseware_id   INT          NOT NULL,
    chunk_index     INT          NOT NULL COMMENT '分块序号（从0开始）',
    content         LONGTEXT     NOT NULL COMMENT '分块文本内容',
    vector_id       VARCHAR(100) NULL     COMMENT 'ChromaDB中对应的向量ID',
    token_count     INT          NOT NULL DEFAULT 0 COMMENT 'Token数量',
    page_ref        VARCHAR(50)  NULL     COMMENT '原文页码引用',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE INDEX idx_cw_chunk (courseware_id, chunk_index),
    INDEX idx_vector (vector_id),

    CONSTRAINT fk_dc_courseware
        FOREIGN KEY (courseware_id) REFERENCES courseware(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档分块表';


-- ============================================================
-- 6. 问答会话表 (qa_conversations)
-- 存储用户的问答对话会话
-- ============================================================
CREATE TABLE qa_conversations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    course_id       INT          NULL COMMENT '关联课程（可为空，支持自由问答）',
    title           VARCHAR(300) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
    message_count   INT          NOT NULL DEFAULT 0 COMMENT '消息数量',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user (user_id),
    INDEX idx_course (course_id),
    INDEX idx_updated (updated_at),

    CONSTRAINT fk_qc_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qc_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答会话表';


-- ============================================================
-- 7. 问答消息表 (qa_messages)
-- 存储每条具体的问答消息（用户问题 & AI回答）
-- ============================================================
CREATE TABLE qa_messages (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id   INT          NOT NULL,
    role              ENUM('user', 'assistant', 'system') NOT NULL,
    content           LONGTEXT     NOT NULL COMMENT '消息内容',
    referenced_chunks JSON         NULL     COMMENT '引用的文档分块 [{"chunk_id":1,"score":0.92}]',
    token_usage       JSON         NULL     COMMENT 'Token消耗 {"prompt":500,"completion":200}',
    response_time_ms  INT          NULL     COMMENT '响应时间(毫秒)',
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_conversation (conversation_id),
    INDEX idx_created (created_at),

    CONSTRAINT fk_qm_conversation
        FOREIGN KEY (conversation_id) REFERENCES qa_conversations(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答消息表';


-- ============================================================
-- 8. 知识点表 (knowledge_points)
-- 存储课程知识点，支持树形层级结构
-- ============================================================
CREATE TABLE knowledge_points (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    course_id       INT          NOT NULL,
    name            VARCHAR(300) NOT NULL COMMENT '知识点名称',
    description     TEXT         NULL     COMMENT '知识点描述/定义',
    level           TINYINT      NOT NULL DEFAULT 1 COMMENT '层级（1=一级, 2=二级, 3=三级...）',
    parent_id       INT          NULL     COMMENT '父知识点ID（自引用，构建树形结构）',
    importance      TINYINT      NOT NULL DEFAULT 3 COMMENT '重要程度 1-5',
    difficulty      TINYINT      NOT NULL DEFAULT 3 COMMENT '难度等级 1-5',
    keywords        VARCHAR(500) NULL     COMMENT '关键词（逗号分隔）',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_course (course_id),
    INDEX idx_parent (parent_id),
    INDEX idx_level (level),
    UNIQUE INDEX idx_course_kp_name (course_id, name),

    CONSTRAINT fk_kp_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_kp_parent
        FOREIGN KEY (parent_id) REFERENCES knowledge_points(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点表';


-- ============================================================
-- 9. 知识点关系表 (knowledge_point_relations)
-- 存储知识点之间的关联关系（构建知识图谱边）
-- ============================================================
CREATE TABLE knowledge_point_relations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    source_kp_id    INT          NOT NULL COMMENT '源知识点ID',
    target_kp_id    INT          NOT NULL COMMENT '目标知识点ID',
    relation_type   ENUM('prerequisite', 'contains', 'related', 'extends', 'applies') NOT NULL DEFAULT 'related'
                    COMMENT '关系类型: prerequisite=先修, contains=包含, related=相关, extends=延伸, applies=应用',
    weight          FLOAT        NOT NULL DEFAULT 1.0 COMMENT '关系权重 (0-1)',
    description     VARCHAR(500) NULL     COMMENT '关系说明',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE INDEX idx_kp_relation (source_kp_id, target_kp_id, relation_type),
    INDEX idx_target (target_kp_id),

    CONSTRAINT fk_kpr_source
        FOREIGN KEY (source_kp_id) REFERENCES knowledge_points(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_kpr_target
        FOREIGN KEY (target_kp_id) REFERENCES knowledge_points(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点关系表';


-- ============================================================
-- 10. 知识点-课件关联表 (kp_courseware)
-- 关联知识点与课件文档（一个知识点可对应多个课件，一个课件可包含多个知识点）
-- ============================================================
CREATE TABLE kp_courseware (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    knowledge_point_id  INT   NOT NULL,
    courseware_id       INT   NOT NULL,
    chunk_id            INT   NULL     COMMENT '关联到具体分块',
    relevance_score     FLOAT NOT NULL DEFAULT 1.0 COMMENT '相关度评分 (0-1)',

    UNIQUE INDEX idx_kp_cw (knowledge_point_id, courseware_id),
    INDEX idx_courseware (courseware_id),
    INDEX idx_chunk (chunk_id),

    CONSTRAINT fk_kpcw_kp
        FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_kpcw_courseware
        FOREIGN KEY (courseware_id) REFERENCES courseware(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_kpcw_chunk
        FOREIGN KEY (chunk_id) REFERENCES document_chunks(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点-课件关联表';


-- ============================================================
-- 11. 反馈表 (feedback)
-- 存储用户对AI回答的评价反馈
-- ============================================================
CREATE TABLE feedback (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    message_id      INT          NOT NULL COMMENT '被评价的消息ID',
    rating          TINYINT      NOT NULL COMMENT '评分 1-5',
    comment         TEXT         NULL     COMMENT '反馈意见',
    feedback_type   ENUM('helpful', 'not_helpful', 'inaccurate', 'incomplete', 'other') NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user (user_id),
    INDEX idx_message (message_id),
    INDEX idx_rating (rating),

    CONSTRAINT fk_fb_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_fb_message
        FOREIGN KEY (message_id) REFERENCES qa_messages(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户反馈表';


-- ============================================================
-- 初始化完成提示
-- ============================================================
-- 共创建 11 张核心表，满足 3NF 范式设计
-- 覆盖: 用户、课程、课件、文档分块、问答会话、问答消息、
--        知识点、知识点关系、知识点-课件关联、用户反馈
-- ============================================================
