package services

import (
	"errors"
	"fmt"
	"time"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/navigator/auth-service/config"
	"github.com/navigator/auth-service/models"
)

type TokenService interface {
	GenerateTokens(user *models.User, sessionID uuid.UUID) (*models.AuthTokens, error)
	ValidateAccessToken(tokenStr string) (*models.TokenClaims, error)
	ValidateRefreshToken(tokenStr string) (*models.RefreshClaims, error)
}

type tokenService struct {
	cfg *config.Config
}

func NewTokenService(cfg *config.Config) TokenService {
	return &tokenService{cfg: cfg}
}

func (s *tokenService) GenerateTokens(user *models.User, sessionID uuid.UUID) (*models.AuthTokens, error) {
	now := time.Now()
	accessExpiry := now.Add(s.cfg.TokenExpiryHours)
	refreshExpiry := now.Add(s.cfg.RefreshExpiryDays)

	accessClaims := &models.TokenClaims{
		UserID:   user.ID,
		Email:    user.Email,
		FullName: user.FullName,
		Role:     user.Role,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "navigator-auth-service",
			Subject:   user.ID.String(),
			Audience:  jwt.ClaimStrings{"navigator-api"},
			ExpiresAt: jwt.NewNumericDate(accessExpiry),
			IssuedAt:  jwt.NewNumericDate(now),
			ID:        uuid.New().String(),
		},
	}

	accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims)
	accessSigned, err := accessToken.SignedString([]byte(s.cfg.JWTSecret))
	if err != nil {
		return nil, fmt.Errorf("failed to sign access token: %w", err)
	}

	refreshClaims := &models.RefreshClaims{
		SessionID: sessionID,
		UserID:    user.ID,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "navigator-auth-service",
			Subject:   user.ID.String(),
			ExpiresAt: jwt.NewNumericDate(refreshExpiry),
			IssuedAt:  jwt.NewNumericDate(now),
			ID:        uuid.New().String(),
		},
	}

	refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims)
	refreshSigned, err := refreshToken.SignedString([]byte(s.cfg.JWTSecret))
	if err != nil {
		return nil, fmt.Errorf("failed to sign refresh token: %w", err)
	}

	return &models.AuthTokens{
		AccessToken:  accessSigned,
		RefreshToken: refreshSigned,
		TokenType:    "Bearer",
		ExpiresIn:    int64(s.cfg.TokenExpiryHours.Seconds()),
	}, nil
}

func (s *tokenService) ValidateAccessToken(tokenStr string) (*models.TokenClaims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &models.TokenClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
		}
		return []byte(s.cfg.JWTSecret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*models.TokenClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("invalid or expired access token")
}

func (s *tokenService) ValidateRefreshToken(tokenStr string) (*models.RefreshClaims, error) {
	token, err := jwt.ParseWithClaims(tokenStr, &models.RefreshClaims{}, func(t *jwt.Token) (interface{}, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
		}
		return []byte(s.cfg.JWTSecret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*models.RefreshClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("invalid or expired refresh token")
}
