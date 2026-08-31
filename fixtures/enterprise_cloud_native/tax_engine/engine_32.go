package taxengine32

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction32 string

const (
	JurisdictionUS32 TaxJurisdiction32 = "US_FEDERAL"
	JurisdictionEU32 TaxJurisdiction32 = "EU_VAT"
	JurisdictionAPAC32 TaxJurisdiction32 = "APAC_GST"
)

type TaxAssessment32 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction32  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine32 struct {
	rates map[TaxJurisdiction32]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine32() *TaxCalculatorEngine32 {
	return &TaxCalculatorEngine32{
		rates: map[TaxJurisdiction32]float64{
			JurisdictionUS32:   0.0825,
			JurisdictionEU32:   0.2000,
			JurisdictionAPAC32: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine32) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction32, amount float64) (*TaxAssessment32, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment32{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
