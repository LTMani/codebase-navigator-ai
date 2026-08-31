package main

import (
	"fmt"
	"log"
	"github.com/gin-gonic/gin"
	"github.com/navigator/auth-service/config"
	"github.com/navigator/auth-service/controllers"
	"github.com/navigator/auth-service/middleware"
	"github.com/navigator/auth-service/models"
	"github.com/navigator/auth-service/repository"
	"github.com/navigator/auth-service/services"
	gorm.io/driver/postgres"
	gorm.io/gorm"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Configuration error: %v", err)
	}

	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Printf("Warning: Database connection failed: %v. Running in detached mode.", err)
	} else {
		_ = db.AutoMigrate(&models.User{}, &models.Session{}, &models.AuditLog{})
	}

	pwdService := services.NewPasswordService(12)
	tokenService := services.NewTokenService(cfg)
	userRepo := repository.NewUserRepository(db)
	sessionRepo := repository.NewSessionRepository(db)

	authCtl := controllers.NewAuthController(userRepo, sessionRepo, tokenService, pwdService)
	userCtl := controllers.NewUserController(userRepo)

	r := gin.Default()
	ratelimiter := middleware.NewRateLimiter(60, 100)
	r.Use(ratelimiter.Middleware())

	api := r.Group("/api/v1")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/register", authCtl.Register)
			auth.POST("/login", authCtl.Login)
			auth.POST("/refresh", authCtl.Refresh)
		}

		protected := api.Group("/")
		protected.Use(middleware.JWTMiddleware(tokenService))
		{
			protected.GET("/profile", userCtl.GetProfile)
			adminOnly := protected.Group("/admin")
			adminOnly.Use(middleware.RequireRoles(models.RoleAdmin))
			{
				adminOnly.GET("/users", userCtl.ListUsers)
				adminOnly.PUT("/users/:id/role", userCtl.UpdateUserRole)
			}
		}
	}

	log.Printf("Starting Go Auth Microservice on port %d...", cfg.Port)
	_ = r.Run(fmt.Sprintf(":%d", cfg.Port))
}
