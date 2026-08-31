package tests

import (
	"testing"
	"github.com/google/uuid"
	"github.com/navigator/auth-service/config"
	"github.com/navigator/auth-service/models"
	"github.com/navigator/auth-service/services"
	"github.com/stretchr/testify/assert"
)

func TestPasswordService(t *testing.T) {
	pwdService := services.NewPasswordService(4)

	password := "StrongP@ssw0rd123!"
	hash, err := pwdService.HashPassword(password)
	assert.NoError(t, err)
	assert.NotEmpty(t, hash)

	err = pwdService.ComparePassword(hash, password)
	assert.NoError(t, err)

	err = pwdService.ComparePassword(hash, "WrongPassword!")
	assert.Error(t, err)

	assert.NoError(t, pwdService.ValidateStrength("Valid@123A"))
	assert.Error(t, pwdService.ValidateStrength("short"))
	assert.Error(t, pwdService.ValidateStrength("nouppercase123!"))
}

func TestTokenService(t *testing.T) {
	cfg := &config.Config{
		JWTSecret:         "test-secret-key-12345",
		TokenExpiryHours:  24,
		RefreshExpiryDays: 7,
	}
	tokenService := services.NewTokenService(cfg)

	user := &models.User{
		ID:       uuid.New(),
		Email:    "developer@navigator.ai",
		FullName: "Test Developer",
		Role:     models.RoleDeveloper,
	}

	sessionID := uuid.New()
	tokens, err := tokenService.GenerateTokens(user, sessionID)
	assert.NoError(t, err)
	assert.NotEmpty(t, tokens.AccessToken)
	assert.NotEmpty(t, tokens.RefreshToken)

	claims, err := tokenService.ValidateAccessToken(tokens.AccessToken)
	assert.NoError(t, err)
	assert.Equal(t, user.Email, claims.Email)
	assert.Equal(t, user.Role, claims.Role)
}
