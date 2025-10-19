CREATE TABLE "user" (
  id UUID PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE course (
  id UUID PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  level VARCHAR(20) CHECK (level IN ('básico', 'intermedio', 'avanzado')) NOT NULL,
  order_in_level INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE lesson (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES course(id) ON DELETE CASCADE,
  content_type VARCHAR(10) CHECK (content_type IN ('video', 'texto')) NOT NULL,
  title TEXT,
  content_url VARCHAR(200),
  text_content TEXT,
  order_in_course INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_progress (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
  lesson_id UUID REFERENCES lesson(id) ON DELETE CASCADE,
  last_accessed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE exam (
  id UUID PRIMARY KEY,
  title TEXT,
  description TEXT,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_exam_result (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
  exam_id UUID REFERENCES exam(id) ON DELETE CASCADE,
  total_score DECIMAL(5,2),
  level_assigned VARCHAR(20) CHECK (level_assigned IN ('basic', 'intermediate', 'advanced')),
  taken_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE questions (
  id UUID PRIMARY KEY,
  question_text TEXT NOT NULL,
  level VARCHAR(20) CHECK (level IN ('basic', 'intermediate', 'advanced')),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE answer (
  id UUID PRIMARY KEY,
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
  answer_text TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
