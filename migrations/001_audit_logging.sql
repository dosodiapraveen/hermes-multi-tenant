-- Migration: Add audit logging infrastructure
-- Description: Adds audit_logs table and enhances activity_logs with request correlation
-- Date: 2026-08-12

-- Add new columns to activity_logs table
ALTER TABLE activity_logs
  ADD COLUMN IF NOT EXISTS request_id TEXT,
  ADD COLUMN IF NOT EXISTS ip_address TEXT,
  ADD COLUMN IF NOT EXISTS admin_id TEXT;

-- Create audit_logs table for security events
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('info','warning','error','critical')),
    user_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    request_id TEXT,
    admin_email TEXT,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin ON audit_logs(admin_email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip ON audit_logs(ip_address);

-- Create indexes for activity_logs
CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created ON activity_logs(created_at DESC);

-- Grant necessary permissions (adjust role name as needed)
-- GRANT SELECT, INSERT ON audit_logs TO hermes;
-- GRANT USAGE, SELECT ON SEQUENCE audit_logs_id_seq TO hermes;

COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for security events, authentication, and administrative actions';
COMMENT ON COLUMN audit_logs.event_type IS 'Type of event (login_success, admin_action, etc.)';
COMMENT ON COLUMN audit_logs.severity IS 'Event severity level: info, warning, error, critical';
COMMENT ON COLUMN audit_logs.details IS 'Additional event-specific metadata as JSON';
COMMENT ON COLUMN audit_logs.request_id IS 'Correlation ID for tracking requests across services';
