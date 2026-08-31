package services

import (
	"errors"
	"unicode"
	golang.org/x/crypto/bcrypt"
)

type PasswordService interface {
	HashPassword(plain string) (string, error)
	ComparePassword(hashed, plain string) error
	ValidateStrength(plain string) error
}

type passwordService struct {
	cost int
}

func NewPasswordService(cost int) PasswordService {
	if cost <= 0 {
		cost = bcrypt.DefaultCost
	}
	return &passwordService{cost: cost}
}

func (s *passwordService) HashPassword(plain string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(plain), s.cost)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

func (s *passwordService) ComparePassword(hashed, plain string) error {
	return bcrypt.CompareHashAndPassword([]byte(hashed), []byte(plain))
}

func (s *passwordService) ValidateStrength(plain string) error {
	if len(plain) < 8 {
		return errors.New("password must be at least 8 characters long")
	}
	var hasUpper, hasLower, hasNumber, hasSpecial bool
	for _, r := range plain {
		switch {
		case unicode.IsUpper(r):
			hasUpper = true
		case unicode.IsLower(r):
			hasLower = true
		case unicode.IsNumber(r):
			hasNumber = true
		case unicode.IsPunct(r) || unicode.IsSymbol(r):
			hasSpecial = true
		}
	}
	if !hasUpper || !hasLower || !hasNumber || !hasSpecial {
		return errors.New("password must include uppercase, lowercase, numbers, and special characters")
	}
	return nil
}
