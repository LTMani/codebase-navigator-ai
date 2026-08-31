package middleware

import (
	"net/http"
	"sync"
	"time"
	"github.com/gin-gonic/gin"
)

type rateBucket struct {
	tokens    int
	lastCheck time.Time
}

type RateLimiter struct {
	rate       int
	capacity   int
	mu         sync.Mutex
	ipBuckets  map[string]*rateBucket
}

func NewRateLimiter(ratePerMin, capacity int) *RateLimiter {
	return &RateLimiter{
		rate:      ratePerMin,
		capacity:  capacity,
		ipBuckets: make(map[string]*rateBucket),
	}
}

func (rl *RateLimiter) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		ip := c.ClientIP()
		rl.mu.Lock()
		bucket, exists := rl.ipBuckets[ip]
		now := time.Now()
		if !exists {
			bucket = &rateBucket{tokens: rl.capacity, lastCheck: now}
			rl.ipBuckets[ip] = bucket
		} else {
			elapsed := now.Sub(bucket.lastCheck).Minutes()
			bucket.tokens += int(elapsed * float64(rl.rate))
			if bucket.tokens > rl.capacity {
				bucket.tokens = rl.capacity
			}
			bucket.lastCheck = now
		}

		if bucket.tokens <= 0 {
			rl.mu.Unlock()
			c.JSON(http.StatusTooManyRequests, gin.H{"error": "rate limit exceeded"})
			c.Abort()
			return
		}

		bucket.tokens--
		rl.mu.Unlock()
		c.Next()
	}
}
