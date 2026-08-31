package eventhub15

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage15 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher15 struct {
	brokerAddr string
	buffer     chan EventMessage15
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher15(brokerAddr string, bufferSize int) *EventHubPublisher15 {
	return &EventHubPublisher15{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage15, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher15) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage15{
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
