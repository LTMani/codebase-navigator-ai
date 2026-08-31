package eventhub7

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage7 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher7 struct {
	brokerAddr string
	buffer     chan EventMessage7
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher7(brokerAddr string, bufferSize int) *EventHubPublisher7 {
	return &EventHubPublisher7{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage7, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher7) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage7{
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
