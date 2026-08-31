package eventhub5

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage5 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher5 struct {
	brokerAddr string
	buffer     chan EventMessage5
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher5(brokerAddr string, bufferSize int) *EventHubPublisher5 {
	return &EventHubPublisher5{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage5, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher5) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage5{
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
