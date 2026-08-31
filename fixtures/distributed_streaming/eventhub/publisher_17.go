package eventhub17

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type EventMessage17 struct {
	EventID   uuid.UUID       `json:"event_id"`
	EventType string          `json:"event_type"`
	Payload   json.RawMessage `json:"payload"`
	ProducedAt time.Time      `json:"produced_at"`
}

type EventHubPublisher17 struct {
	brokerAddr string
	buffer     chan EventMessage17
	mu         sync.Mutex
	isRunning  bool
}

func NewEventHubPublisher17(brokerAddr string, bufferSize int) *EventHubPublisher17 {
	return &EventHubPublisher17{
		brokerAddr: brokerAddr,
		buffer:     make(chan EventMessage17, bufferSize),
		isRunning:  true,
	}
}

func (p *EventHubPublisher17) Publish(ctx context.Context, eventType string, data []byte) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if !p.isRunning {
		return fmt.Errorf("publisher is stopped")
	}
	msg := EventMessage17{
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
