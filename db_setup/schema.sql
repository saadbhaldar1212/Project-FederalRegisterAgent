CREATE DATABASE IF NOT EXISTS federal_registry_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE federal_registry_db;

CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_number VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    type VARCHAR(100),
    abstract TEXT,
    publication_date DATE,
    agencies JSON,
    cfr_references JSON,
    document_url TEXT,
    pdf_url TEXT,
    raw_text_url TEXT,
    president VARCHAR(255) NULL,
    executive_order_number VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Optional: Indexes for faster searching
CREATE INDEX idx_publication_date ON documents (publication_date);
CREATE INDEX idx_type ON documents (type);
CREATE INDEX idx_president ON documents (president);


-- Full-text search on title and abstract might be beneficial
-- ALTER TABLE documents ADD FULLTEXT(title, abstract);