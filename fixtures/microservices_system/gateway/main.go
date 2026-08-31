package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

type GatewayConfig struct {
	Port         int
	AuthService  string
	OrderService string
	Timeout      time.Duration
}

func main() {
	cfg := GatewayConfig{
		Port:         8080,
		AuthService:  "http://auth-service:5001",
		OrderService: "http://order-service:5002",
		Timeout:      10 * time.Second,
	}

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"healthy","service":"api_gateway"}`)
	})

	http.HandleFunc("/api/v1/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Gateway Proxying request: %s %s", r.Method, r.URL.Path)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"message":"Routed through API Gateway"}`)
	})

	log.Printf("API Gateway listening on :%d", cfg.Port)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", cfg.Port), nil); err != nil {
		log.Fatalf("Gateway failure: %v", err)
	}
}
