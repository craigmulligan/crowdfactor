CREATE TABLE IF NOT EXISTS training_log (timestamp TEXT, score REAL, name TEXT);
CREATE INDEX IF NOT EXISTS training_log_timestamp_idx ON training_log(timestamp);
CREATE INDEX IF NOT EXISTS training_log_name_idx ON training_log(name);
