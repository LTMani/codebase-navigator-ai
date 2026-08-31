package eventhub10

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage10 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher10 struct {
	brokerAddr string
	buffer     chan EventMessage10
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher10(brokerAddr string, bufferSize int) *EventHubPublisher10 {
	return &EventHubPublisher10{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage10, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher10) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage10{
		EventID:   uuid.New(),
		EventType: eventType,
		Payload:   json.RawMessage(data),
		ProducedAt: time.Now(),
	}
	select {
	case p.buffer <- msg:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	default:
		return fmt.Errorf("publish queue buffer full")
	}
}
