-- migrate:up
-- Bees and repeaters number their serials independently, so bee 10 and repeater 10 are two different
-- devices. A serial is unique within its device type, not across the whole table.
--
-- The baseline declared the column UNIQUE inline, so the constraint carries a generated name
-- (normally devices_dev_sn_key). Drop whichever single-column unique constraint sits on dev_sn
-- rather than trusting that name.
DO $$
DECLARE
    con TEXT;
BEGIN
    FOR con IN
        SELECT c.conname
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
        WHERE c.conrelid = 'devices'::regclass
          AND c.contype = 'u'
          AND array_length(c.conkey, 1) = 1
          AND a.attname = 'dev_sn'
    LOOP
        EXECUTE format('ALTER TABLE devices DROP CONSTRAINT %I', con);
    END LOOP;
END $$;

ALTER TABLE devices DROP CONSTRAINT IF EXISTS devices_dev_sn_device_type_key;
ALTER TABLE devices ADD CONSTRAINT devices_dev_sn_device_type_key UNIQUE (dev_sn, device_type);

-- migrate:down
-- Forward-only. To undo, restore the backup taken before migrating (data/backups/). Note that once a bee and a
-- repeater share a serial, the old single-column constraint can no longer be restored without removing one of them.
