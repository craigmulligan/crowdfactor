CREATE TABLE IF NOT EXISTS crowd_log (timestamp TEXT PRIMARY KEY, crowd_count INTEGER, surf_rating TEXT, spot_id TEXT, model_version INTEGER);
CREATE INDEX IF NOT EXISTS crowd_log_crowd_count_idx ON crowd_log(crowd_count);
CREATE INDEX IF NOT EXISTS crowd_log_spot_id_idx ON crowd_log(spot_id);
CREATE INDEX IF NOT EXISTS crowd_log_surf_rating_idx ON crowd_log(surf_rating);
