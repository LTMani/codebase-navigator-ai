package models

import (
	"time"
	"github.com/google/uuid"
	gorm.io/gorm"
)

type UserRole string

const (
	RoleAdmin     UserRole = "ADMIN"
	RoleDeveloper UserRole = "DEVELOPER"
	RoleViewer    UserRole = "VIEWER"
	RoleAuditor   UserRole = "AUDITOR"
)

type User struct {
	ID                  uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	Email               string         `gorm:"type:varchar(255);uniqueIndex;not null" json:"email" binding:"required,email"`
	PasswordHash        string         `gorm:"type:varchar(255);not null" json:"-"`
	FullName            string         `gorm:"type:varchar(128);not null" json:"full_name" binding:"required,min=2,max=128"`
	Role                UserRole       `gorm:"type:varchar(32);default:'DEVELOPER';not null" json:"role"`
	IsActive            bool           `gorm:"default:true;not null" json:"is_active"`
	IsMfaEnabled        bool           `gorm:"default:false;not null" json:"is_mfa_enabled"`
	MfaSecret           string         `gorm:"type:varchar(64)" json:"-"`
	LastLoginAt         *time.Time     `json:"last_login_at"`
	FailedLoginAttempts int            `gorm:"default:0;not null" json:"failed_login_attempts"`
	LockedUntil         *time.Time     `json:"locked_until"`
	CreatedAt           time.Time      `json:"created_at"`
	UpdatedAt           time.Time      `json:"updated_at"`
	DeletedAt           gorm.DeletedAt `gorm:"index" json:"-"`
}

func (u *User) IsLocked() bool {
	if u.LockedUntil == nil {
		return false
	}
	return time.Now().Before(*u.LockedUntil)
}

func (u *User) ResetLock() {
	u.FailedLoginAttempts = 0
	u.LockedUntil = nil
}

func (u *User) IncrementFailedAttempts(maxAttempts int, lockoutDuration time.Duration) {
	u.FailedLoginAttempts++
	if u.FailedLoginAttempts >= maxAttempts {
		lockTime := time.Now().Add(lockoutDuration)
		u.LockedUntil = &lockTime
	}
}
