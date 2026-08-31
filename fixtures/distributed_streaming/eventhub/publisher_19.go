package eventhub19

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage19 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher19 struct {
	brokerAddr string
	buffer     chan EventMessage19
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher19(brokerAddr string, bufferSize int) *EventHubPublisher19 {
	return &EventHubPublisher19{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage19, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher19) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage19{
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
