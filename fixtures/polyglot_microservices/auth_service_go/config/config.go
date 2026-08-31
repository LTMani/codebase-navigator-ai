package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	Port               int
	Environment        string
	DatabaseURL        string
	JWTSecret          string
	TokenExpiryHours   time.Duration
	RefreshExpiryDays  time.Duration
	MaxFailedAttempts  int
	LockoutDurationMin time.Duration
	EnableAuditLog     bool
}

func LoadConfig() (*Config, error) {
	port, err := strconv.Atoi(getEnvOrDefault("PORT", "8081"))
	if err != nil {
		return nil, fmt.Errorf("invalid PORT environment variable: %w", err)
	}

	tokenExp, err := strconv.Atoi(getEnvOrDefault("JWT_EXPIRY_HOURS", "24"))
	if err != nil {
		tokenExp = 24
	}

	refreshExp, err := strconv.Atoi(getEnvOrDefault("REFRESH_EXPIRY_DAYS", "7"))
	if err != nil {
		refreshExp = 7
	}

	maxAttempts, err := strconv.Atoi(getEnvOrDefault("MAX_FAILED_ATTEMPTS", "5"))
	if err != nil {
		maxAttempts = 5
	}

	lockoutMin, err := strconv.Atoi(getEnvOrDefault("LOCKOUT_MINUTES", "15"))
	if err != nil {
		lockoutMin = 15
	}

	secret := os.Getenv("JWT_SECRET")
	if secret == "" {
		secret = "default-development-jwt-super-secret-key-change-in-prod"
	}

	return &Config{
		Port:               port,
		Environment:        getEnvOrDefault("ENV", "development"),
		DatabaseURL:        getEnvOrDefault("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/auth_db?sslmode=disable"),
		JWTSecret:          secret,
		TokenExpiryHours:   time.Duration(tokenExp) * time.Hour,
		RefreshExpiryDays:  time.Duration(refreshExp) * 24 * time.Hour,
		MaxFailedAttempts:  maxAttempts,
		LockoutDurationMin: time.Duration(lockoutMin) * time.Minute,
		EnableAuditLog:     getEnvOrDefault("ENABLE_AUDIT_LOG", "true") == "true",
	}, nil
}

func getEnvOrDefault(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok && val != "" {
		return val
	}
	return fallback
}
