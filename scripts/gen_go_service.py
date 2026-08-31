import os
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    print(f'[GO SERVICE] {rel_path:<50} ({loc:>5} LOC)')
    return loc

write_f('fixtures/polyglot_microservices/auth_service_go/go.mod', '''module github.com/navigator/auth-service

go 1.22

require (
	github.com/gin-gonic/gin v1.9.1
	github.com/golang-jwt/jwt/v5 v5.2.0
	github.com/google/uuid v1.6.0
	golang.org/x/crypto v0.20.0
	gorm.io/gorm v1.25.7
	gorm.io/driver/postgres v1.5.7
)
''')

write_f('fixtures/polyglot_microservices/auth_service_go/main.go', '''package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/navigator/auth-service/config"
	"github.com/navigator/auth-service/controllers"
	"github.com/navigator/auth-service/middleware"
	"github.com/navigator/auth-service/repository"
	"github.com/navigator/auth-service/services"
)

// Application holds dependencies for the Auth Microservice.
type Application struct {
	Config     *config.Config
	UserRepo   repository.UserRepository
	SessionRepo repository.SessionRepository
	TokenSvc   services.TokenService
	PasswordSvc services.PasswordService
	MFASvc     services.MFAService
	AuthCtrl   *controllers.AuthController
	UserCtrl   *controllers.UserController
}

// NewApplication initializes all layers via dependency injection.
func NewApplication(cfg *config.Config) *Application {
	userRepo := repository.NewMemoryUserRepository()
	sessionRepo := repository.NewMemorySessionRepository()
	tokenSvc := services.NewJWTTokenService(cfg.JWTSecret, cfg.JWTExpiry)
	passwordSvc := services.NewBcryptPasswordService(12)
	mfaSvc := services.NewTOTPMFAService("CodebaseNavigator")

	authCtrl := controllers.NewAuthController(userRepo, sessionRepo, tokenSvc, passwordSvc, mfaSvc)
	userCtrl := controllers.NewUserController(userRepo, passwordSvc)

	return &Application{
		Config:     cfg,
		UserRepo:   userRepo,
		SessionRepo: sessionRepo,
		TokenSvc:   tokenSvc,
		PasswordSvc: passwordSvc,
		MFASvc:     mfaSvc,
		AuthCtrl:   authCtrl,
		UserCtrl:   userCtrl,
	}
}

// SetupRouter binds endpoints and middleware.
func (app *Application) SetupRouter() *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.AuditLogger())
	r.Use(middleware.CORS())
	r.Use(middleware.RateLimiter(100, time.Minute))

	// Health Check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "up", "service": "auth-service"})
	})

	api := r.Group("/api/v1")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/register", app.AuthCtrl.Register)
			auth.POST("/login", app.AuthCtrl.Login)
			auth.POST("/refresh", app.AuthCtrl.RefreshToken)
			auth.POST("/logout", app.AuthCtrl.Logout)
			auth.POST("/verify-mfa", app.AuthCtrl.VerifyMFA)
		}

		protected := api.Group("/users")
		protected.Use(middleware.JWTAuth(app.TokenSvc))
		{
			protected.GET("/me", app.UserCtrl.GetCurrentUser)
			protected.PUT("/profile", app.UserCtrl.UpdateProfile)
			protected.POST("/change-password", app.UserCtrl.ChangePassword)
			protected.POST("/enable-mfa", app.UserCtrl.EnableMFA)
		}
	}

	return r
}

func main() {
	cfg := config.Load()
	app := NewApplication(cfg)
	router := app.SetupRouter()

	srv := &http.Server{
		Addr:     ":" + cfg.Port,
		Handler: router,
	}

	go func() {
		log.Printf("Auth Service starting on port %s", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down Auth Service...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced shutdown: %v", err)
	}
	log.Println("Auth Service exited cleanly")
}
''')
