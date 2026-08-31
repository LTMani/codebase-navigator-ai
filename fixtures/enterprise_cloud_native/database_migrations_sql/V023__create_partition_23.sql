-- Migration Script 023: Create Enterprise Partitioned Table 23
CREATE TABLE IF NOT EXISTS enterprise_telemetry_partition_23 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_code VARCHAR(64) NOT NULL DEFAULT 'SRV_23',
    latency_ms DOUBLE PRECISION NOT NULL,
    status_code INT NOT NULL DEFAULT 200,
    payload_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telemetry_p23_service ON enterprise_telemetry_partition_23(service_code);
CREATE INDEX IF NOT EXISTS idx_telemetry_p23_created ON enterprise_telemetry_partition_23(created_at);

CREATE OR REPLACE FUNCTION record_telemetry_event_23(
    p_service_code VARCHAR,
    p_latency DOUBLE PRECISION,
    p_status INT
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO enterprise_telemetry_partition_23 (service_code, latency_ms, status_code)
    VALUES (p_service_code, p_latency, p_status)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;
