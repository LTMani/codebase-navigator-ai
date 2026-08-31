package eventhub11

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage11 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher11 struct {
	brokerAddr string
	buffer     chan EventMessage11
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher11(brokerAddr string, bufferSize int) *EventHubPublisher11 {
	return &EventHubPublisher11{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage11, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher11) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage11{
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
