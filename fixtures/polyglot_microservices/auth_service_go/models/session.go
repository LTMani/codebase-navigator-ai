package models

import (
	"time"
	"github.com/google/uuid"
	gorm.io/gorm"
)

type SessionStatus string

const (
	SessionActive   SessionStatus = "ACTIVE"
	SessionRevoked  SessionStatus = "REVOKED"
	SessionExpired  SessionStatus = "EXPIRED"
)

type Session struct {
	ID           uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	UserID       uuid.UUID      `gorm:"type:uuid;not null;index" json:"user_id"`
	User         User           `gorm:"foreignKey:UserID;constraint:OnDelete:CASCADE" json:"user,omitempty"`
	RefreshToken string         `gorm:"type:varchar(512);uniqueIndex;not null" json:"refresh_token"`
	UserAgent    string         `gorm:"type:varchar(512)" json:"user_agent"`
	ClientIP     string         `gorm:"type:varchar(64)" json:"client_ip"`
	Status       SessionStatus  `gorm:"type:varchar(32);default:'ACTIVE';not null" json:"status"`
	ExpiresAt    time.Time      `gorm:"not null" json:"expires_at"`
	CreatedAt    time.Time      `json:"created_at"`
	UpdatedAt    time.Time      `json:"updated_at"`
	DeletedAt    gorm.DeletedAt `gorm:"index" json:"-"`
}

func (s *Session) IsValid() bool {
	return s.Status == SessionActive && time.Now().Before(s.ExpiresAt)
}

func (s *Session) Revoke() {
	s.Status = SessionRevoked
}
