-- migrate:up
-- Repeaters have no GNSS, so their position is set by hand (like HQ) and kept on the device row.
-- Bees report their own position in location_events and never use these columns. The site_ prefix keeps
-- them from colliding with location_events.latitude/longitude in the many queries that join the two tables.
ALTER TABLE devices
    ADD COLUMN IF NOT EXISTS site_latitude  DOUBLE PRECISION CHECK (site_latitude  BETWEEN -90  AND 90),
    ADD COLUMN IF NOT EXISTS site_longitude DOUBLE PRECISION CHECK (site_longitude BETWEEN -180 AND 180);

ALTER TABLE devices DROP CONSTRAINT IF EXISTS devices_location_pair;
ALTER TABLE devices ADD CONSTRAINT devices_location_pair
    CHECK ((site_latitude IS NULL) = (site_longitude IS NULL));

ALTER TABLE devices DROP CONSTRAINT IF EXISTS devices_location_repeater_only;
ALTER TABLE devices ADD CONSTRAINT devices_location_repeater_only
    CHECK (site_latitude IS NULL OR device_type = 'repeater');

-- migrate:down
-- Forward-only. To undo, restore the backup taken before migrating (data/backups/).
