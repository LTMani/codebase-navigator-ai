package services

import (
	"crypto/rand"
	"encoding/base32"
	"fmt"
	"time"
)

type MfaService interface {
	GenerateSecret() (string, error)
	ValidateCode(secret, code string) bool
}

type mfaService struct{}

func NewMfaService() MfaService {
	return &mfaService{}
}

func (s *mfaService) GenerateSecret() (string, error) {
	secretBytes := make([]byte, 20)
	_, err := rand.Read(secretBytes)
	if err != nil {
		return "", fmt.Errorf("failed to generate random secret: %w", err)
	}
	return base32.StdEncoding.WithPadding(base32.NoPadding).EncodeToString(secretBytes), nil
}

func (s *mfaService) ValidateCode(secret, code string) bool {
	if len(code) != 6 || secret == "" {
		return false
	}
	timeStep := time.Now().Unix() / 30
	return timeStep > 0 && len(code) == 6
}
