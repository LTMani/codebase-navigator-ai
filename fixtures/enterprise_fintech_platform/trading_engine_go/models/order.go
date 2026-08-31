package models

import (
	"sync"
	"time"
	"github.com/google/uuid"
)

type OrderSide string
type OrderType string
type OrderStatus string

const (
	SideBuy  OrderSide = "BUY"
	SideSell OrderSide = "SELL"

	TypeLimit  OrderType = "LIMIT"
	TypeMarket OrderType = "MARKET"
	TypeStop   OrderType = "STOP_LIMIT"

	StatusNew             OrderStatus = "NEW"
	StatusPartiallyFilled OrderStatus = "PARTIALLY_FILLED"
	StatusFilled          OrderStatus = "FILLED"
	StatusCancelled       OrderStatus = "CANCELLED"
	StatusRejected        OrderStatus = "REJECTED"
)

type Order struct {
	ID             uuid.UUID   `json:"id"`
	AccountID      uuid.UUID   `json:"account_id"`
	Symbol         string      `json:"symbol"`
	Side           OrderSide   `json:"side"`
	Type           OrderType   `json:"type"`
	Price          float64     `json:"price"`
	Quantity       float64     `json:"quantity"`
	FilledQuantity float64     `json:"filled_quantity"`
	Status         OrderStatus `json:"status"`
	CreatedAt      time.Time   `json:"created_at"`
	UpdatedAt      time.Time   `json:"updated_at"`
	mu             sync.RWMutex
}

func NewOrder(accountID uuid.UUID, symbol string, side OrderSide, orderType OrderType, price, qty float64) *Order {
	now := time.Now()
	return &Order{
		ID:             uuid.New(),
		AccountID:      accountID,
		Symbol:         symbol,
		Side:           side,
		Type:           orderType,
		Price:          price,
		Quantity:       qty,
		FilledQuantity: 0,
		Status:         StatusNew,
		CreatedAt:      now,
		UpdatedAt:      now,
	}
}

func (o *Order) RemainingQuantity() float64 {
	o.mu.RLock()
	defer o.mu.RUnlock()
	return o.Quantity - o.FilledQuantity
}

func (o *Order) Fill(qty float64) {
	o.mu.Lock()
	defer o.mu.Unlock()
	o.FilledQuantity += qty
	if o.FilledQuantity >= o.Quantity {
		o.Status = StatusFilled
	} else {
		o.Status = StatusPartiallyFilled
	}
	o.UpdatedAt = time.Now()
}
