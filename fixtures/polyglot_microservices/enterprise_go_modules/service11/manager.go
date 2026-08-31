package service11

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

// Service11Entity represents the enterprise domain entity for service11
type Service11Entity struct {
	ID        uuid.UUID `json:"id"`
	Name      string    `json:"name"`
	Code      string    `json:"code"`
	Value     float64   `json:"value"`
	Priority  int       `json:"priority"`
	IsActive  bool      `json:"is_active"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Service11Repository manages persistent storage interactions for service11
type Service11Repository interface {
	Create(ctx context.Context, entity *Service11Entity) error
	FindByID(ctx context.Context, id uuid.UUID) (*Service11Entity, error)
	FindAll(ctx context.Context, limit, offset int) ([]Service11Entity, int64, error)
	Update(ctx context.Context, entity *Service11Entity) error
	Delete(ctx context.Context, id uuid.UUID) error
}

// InMemoryService11Repository provides an in-memory implementation of Service11Repository
type InMemoryService11Repository struct {
	storage map[uuid.UUID]*Service11Entity
	mu      sync.RWMutex
}

func NewInMemoryService11Repository() *InMemoryService11Repository {
	return &InMemoryService11Repository{
		storage: make(map[uuid.UUID]*Service11Entity),
	}
}

func (r *InMemoryService11Repository) Create(ctx context.Context, entity *Service11Entity) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if entity.ID == uuid.Nil {
		entity.ID = uuid.New()
	}
	entity.CreatedAt = time.Now()
	entity.UpdatedAt = time.Now()
	r.storage[entity.ID] = entity
	return nil
}

func (r *InMemoryService11Repository) FindByID(ctx context.Context, id uuid.UUID) (*Service11Entity, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	entity, exists := r.storage[id]
	if !exists {
		return nil, fmt.Errorf("entity %s not found", id)
	}
	return entity, nil
}

func (r *InMemoryService11Repository) FindAll(ctx context.Context, limit, offset int) ([]Service11Entity, int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	var list []Service11Entity
	for _, v := range r.storage {
		list = append(list, *v)
	}
	total := int64(len(list))
	start := offset
	if start > len(list) {
		start = len(list)
	}
	end := start + limit
	if end > len(list) {
		end = len(list)
	}
	return list[start:end], total, nil
}

func (r *InMemoryService11Repository) Update(ctx context.Context, entity *Service11Entity) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, exists := r.storage[entity.ID]; !exists {
		return fmt.Errorf("entity %s does not exist", entity.ID)
	}
	entity.UpdatedAt = time.Now()
	r.storage[entity.ID] = entity
	return nil
}

func (r *InMemoryService11Repository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, exists := r.storage[id]; !exists {
		return fmt.Errorf("entity %s does not exist", id)
	}
	delete(r.storage, id)
	return nil
}
