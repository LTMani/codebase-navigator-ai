package controllers

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/navigator/auth-service/models"
	"github.com/navigator/auth-service/repository"
	"github.com/navigator/auth-service/services"
)

type AuthController struct {
	userRepo     repository.UserRepository
	sessionRepo  repository.SessionRepository
	tokenService services.TokenService
	pwdService   services.PasswordService
}

func NewAuthController(
	uRepo repository.UserRepository,
	sRepo repository.SessionRepository,
	tService services.TokenService,
	pService services.PasswordService,
) *AuthController {
	return &AuthController{
		userRepo:     uRepo,
		sessionRepo:  sRepo,
		tokenService: tService,
		pwdService:   pService,
	}
}

type RegisterRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=8"`
	FullName string `json:"full_name" binding:"required"`
}

type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

type RefreshRequest struct {
	RefreshToken string `json:"refresh_token" binding:"required"`
}

func (ctl *AuthController) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := ctl.pwdService.ValidateStrength(req.Password); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	existing, err := ctl.userRepo.FindByEmail(c.Request.Context(), req.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "database error"})
		return
	}
	if existing != nil {
		c.JSON(http.StatusConflict, gin.H{"error": "email already registered"})
		return
	}

	hashed, err := ctl.pwdService.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to secure password"})
		return
	}

	user := &models.User{
		Email:        req.Email,
		PasswordHash: hashed,
		FullName:     req.FullName,
		Role:         models.RoleDeveloper,
		IsActive:     true,
	}

	if err := ctl.userRepo.Create(c.Request.Context(), user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create user account"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "user registered successfully", "user": user})
}

func (ctl *AuthController) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := ctl.userRepo.FindByEmail(c.Request.Context(), req.Email)
	if err != nil || user == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid email or password"})
		return
	}

	if user.IsLocked() {
		c.JSON(http.StatusForbidden, gin.H{"error": "account temporarily locked due to excessive failed attempts"})
		return
	}

	if err := ctl.pwdService.ComparePassword(user.PasswordHash, req.Password); err != nil {
		user.IncrementFailedAttempts(5, 15)
		_ = ctl.userRepo.Update(c.Request.Context(), user)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid email or password"})
		return
	}

	user.ResetLock()
	_ = ctl.userRepo.Update(c.Request.Context(), user)

	sessionID := uuid.New()
	tokens, err := ctl.tokenService.GenerateTokens(user, sessionID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "token generation failed"})
		return
	}

	session := &models.Session{
		ID:           sessionID,
		UserID:       user.ID,
		RefreshToken: tokens.RefreshToken,
		UserAgent:    c.Request.UserAgent(),
		ClientIP:     c.ClientIP(),
		Status:       models.SessionActive,
	}
	_ = ctl.sessionRepo.Create(c.Request.Context(), session)

	c.JSON(http.StatusOK, tokens)
}

func (ctl *AuthController) Refresh(c *gin.Context) {
	var req RefreshRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	claims, err := ctl.tokenService.ValidateRefreshToken(req.RefreshToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid refresh token"})
		return
	}

	session, err := ctl.sessionRepo.FindByToken(c.Request.Context(), req.RefreshToken)
	if err != nil || session == nil || !session.IsValid() {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "session expired or revoked"})
		return
	}

	user, err := ctl.userRepo.FindByID(c.Request.Context(), claims.UserID)
	if err != nil || user == nil || !user.IsActive {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user no longer active"})
		return
	}

	_ = ctl.sessionRepo.RevokeSession(c.Request.Context(), session.ID)

	newSessionID := uuid.New()
	newTokens, err := ctl.tokenService.GenerateTokens(user, newSessionID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to issue new tokens"})
		return
	}

	newSession := &models.Session{
		ID:           newSessionID,
		UserID:       user.ID,
		RefreshToken: newTokens.RefreshToken,
		UserAgent:    c.Request.UserAgent(),
		ClientIP:     c.ClientIP(),
		Status:       models.SessionActive,
	}
	_ = ctl.sessionRepo.Create(c.Request.Context(), newSession)

	c.JSON(http.StatusOK, newTokens)
}
