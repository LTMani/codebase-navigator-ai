package eventhub8

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage8 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher8 struct {
	brokerAddr string
	buffer     chan EventMessage8
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher8(brokerAddr string, bufferSize int) *EventHubPublisher8 {
	return &EventHubPublisher8{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage8, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher8) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage8{
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
