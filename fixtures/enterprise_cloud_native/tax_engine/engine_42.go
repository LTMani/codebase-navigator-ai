package taxengine42

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction42 string

const (
	JurisdictionUS42 TaxJurisdiction42 = "US_FEDERAL"
	JurisdictionEU42 TaxJurisdiction42 = "EU_VAT"
	JurisdictionAPAC42 TaxJurisdiction42 = "APAC_GST"
)

type TaxAssessment42 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction42  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine42 struct {
	rates map[TaxJurisdiction42]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine42() *TaxCalculatorEngine42 {
	return &TaxCalculatorEngine42{
		rates: map[TaxJurisdiction42]float64{
			JurisdictionUS42:   0.0825,
			JurisdictionEU42:   0.2000,
			JurisdictionAPAC42: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine42) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction42, amount float64) (*TaxAssessment42, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment42{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
