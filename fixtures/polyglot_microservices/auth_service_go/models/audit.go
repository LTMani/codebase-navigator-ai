package models

import (
	"time"
	"github.com/google/uuid"
)

type AuditAction string

const (
	ActionLoginSuccess  AuditAction = "LOGIN_SUCCESS"
	ActionLoginFailure  AuditAction = "LOGIN_FAILURE"
	ActionLogout        AuditAction = "LOGOUT"
	ActionPasswordReset AuditAction = "PASSWORD_RESET"
	ActionUserCreated   AuditAction = "USER_CREATED"
	ActionRoleUpdated   AuditAction = "ROLE_UPDATED"
)

type AuditLog struct {
	ID        uuid.UUID   `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	UserID    *uuid.UUID  `gorm:"type:uuid;index" json:"user_id"`
	Action    AuditAction `gorm:"type:varchar(64);not null;index" json:"action"`
	Resource  string      `gorm:"type:varchar(128)" json:"resource"`
	ClientIP  string      `gorm:"type:varchar(64)" json:"client_ip"`
	UserAgent string      `gorm:"type:varchar(512)" json:"user_agent"`
	Details   string      `gorm:"type:text" json:"details"`
	CreatedAt time.Time   `json:"created_at"`
}
