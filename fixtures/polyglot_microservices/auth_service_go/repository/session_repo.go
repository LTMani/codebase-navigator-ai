package repository

import (
	"context"
	"errors"
	"github.com/google/uuid"
	"github.com/navigator/auth-service/models"
	gorm.io/gorm"
)

type SessionRepository interface {
	Create(ctx context.Context, session *models.Session) error
	FindByToken(ctx context.Context, token string) (*models.Session, error)
	RevokeUserSessions(ctx context.Context, userID uuid.UUID) error
	RevokeSession(ctx context.Context, sessionID uuid.UUID) error
}

type sessionRepository struct {
	db *gorm.DB
}

func NewSessionRepository(db *gorm.DB) SessionRepository {
	return &sessionRepository{db: db}
}

func (r *sessionRepository) Create(ctx context.Context, session *models.Session) error {
	return r.db.WithContext(ctx).Create(session).Error
}

func (r *sessionRepository) FindByToken(ctx context.Context, token string) (*models.Session, error) {
	var session models.Session
	err := r.db.WithContext(ctx).Preload("User").Where("refresh_token = ?", token).First(&session).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &session, nil
}

func (r *sessionRepository) RevokeUserSessions(ctx context.Context, userID uuid.UUID) error {
	return r.db.WithContext(ctx).Model(&models.Session{}).
		Where("user_id = ? AND status = ?", userID, models.SessionActive).
		Update("status", models.SessionRevoked).Error
}

func (r *sessionRepository) RevokeSession(ctx context.Context, sessionID uuid.UUID) error {
	return r.db.WithContext(ctx).Model(&models.Session{}).
		Where("id = ?", sessionID).
		Update("status", models.SessionRevoked).Error
}
