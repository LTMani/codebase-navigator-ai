package engine

import (
	"container/heap"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
	"github.com/navigator/trading-engine/models"
)

type TradeExecution struct {
	TradeID       uuid.UUID `json:"trade_id"`
	BuyOrderID    uuid.UUID `json:"buy_order_id"`
	SellOrderID   uuid.UUID `json:"sell_order_id"`
	Symbol        string    `json:"symbol"`
	Price         float64   `json:"price"`
	Quantity      float64   `json:"quantity"`
	ExecutedAt    time.Time `json:"executed_at"`
}

type OrderHeap []*models.Order

func (h OrderHeap) Len() int           { return len(h) }
func (h OrderHeap) Less(i, j int) bool {
	if h[i].Price == h[j].Price {
		return h[i].CreatedAt.Before(h[j].CreatedAt)
	}
	if h[i].Side == models.SideBuy {
		return h[i].Price > h[j].Price // Max-heap for Bids
	}
	return h[i].Price < h[j].Price     // Min-heap for Asks
}
func (h OrderHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *OrderHeap) Push(x interface{}) { *h = append(*h, x.(*models.Order)) }
func (h *OrderHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

type OrderBook struct {
	Symbol   string
	Bids     OrderHeap
	Asks     OrderHeap
	mu       sync.Mutex
	Trades   []TradeExecution
}

func NewOrderBook(symbol string) *OrderBook {
	ob := &OrderBook{
		Symbol: symbol,
		Bids:   make(OrderHeap, 0),
		Asks:   make(OrderHeap, 0),
		Trades: make([]TradeExecution, 0),
	}
	heap.Init(&ob.Bids)
	heap.Init(&ob.Asks)
	return ob
}

func (ob *OrderBook) PlaceOrder(order *models.Order) ([]TradeExecution, error) {
	ob.mu.Lock()
	defer ob.mu.Unlock()

	var executions []TradeExecution

	if order.Side == models.SideBuy {
		executions = ob.matchBuyOrder(order)
		if order.RemainingQuantity() > 0 {
			heap.Push(&ob.Bids, order)
		}
	} else {
		executions = ob.matchSellOrder(order)
		if order.RemainingQuantity() > 0 {
			heap.Push(&ob.Asks, order)
		}
	}

	ob.Trades = append(ob.Trades, executions...)
	return executions, nil
}

func (ob *OrderBook) matchBuyOrder(buyOrder *models.Order) []TradeExecution {
	var trades []TradeExecution
	for ob.Asks.Len() > 0 && buyOrder.RemainingQuantity() > 0 {
		bestAsk := ob.Asks[0]
		if buyOrder.Type == models.TypeLimit && buyOrder.Price < bestAsk.Price {
			break
		}

		matchQty := min(buyOrder.RemainingQuantity(), bestAsk.RemainingQuantity())
		tradePrice := bestAsk.Price

		buyOrder.Fill(matchQty)
		bestAsk.Fill(matchQty)

		trade := TradeExecution{
			TradeID:     uuid.New(),
			BuyOrderID:  buyOrder.ID,
			SellOrderID: bestAsk.ID,
			Symbol:      ob.Symbol,
			Price:       tradePrice,
			Quantity:    matchQty,
			ExecutedAt:  time.Now(),
		}
		trades = append(trades, trade)

		if bestAsk.RemainingQuantity() == 0 {
			heap.Pop(&ob.Asks)
		}
	}
	return trades
}

func (ob *OrderBook) matchSellOrder(sellOrder *models.Order) []TradeExecution {
	var trades []TradeExecution
	for ob.Bids.Len() > 0 && sellOrder.RemainingQuantity() > 0 {
		bestBid := ob.Bids[0]
		if sellOrder.Type == models.TypeLimit && sellOrder.Price > bestBid.Price {
			break
		}

		matchQty := min(sellOrder.RemainingQuantity(), bestBid.RemainingQuantity())
		tradePrice := bestBid.Price

		sellOrder.Fill(matchQty)
		bestBid.Fill(matchQty)

		trade := TradeExecution{
			TradeID:     uuid.New(),
			BuyOrderID:  bestBid.ID,
			SellOrderID: sellOrder.ID,
			Symbol:      ob.Symbol,
			Price:       tradePrice,
			Quantity:    matchQty,
			ExecutedAt:  time.Now(),
		}
		trades = append(trades, trade)

		if bestBid.RemainingQuantity() == 0 {
			heap.Pop(&ob.Bids)
		}
	}
	return trades
}

func (ob *OrderBook) Depth() (float64, float64, error) {
	ob.mu.Lock()
	defer ob.mu.Unlock()

	var bestBid, bestAsk float64
	if ob.Bids.Len() > 0 {
		bestBid = ob.Bids[0].Price
	}
	if ob.Asks.Len() > 0 {
		bestAsk = ob.Asks[0].Price
	}
	return bestBid, bestAsk, nil
}
