package taxengine28

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction28 string

const (
	JurisdictionUS28 TaxJurisdiction28 = "US_FEDERAL"
	JurisdictionEU28 TaxJurisdiction28 = "EU_VAT"
	JurisdictionAPAC28 TaxJurisdiction28 = "APAC_GST"
)

type TaxAssessment28 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction28  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine28 struct {
	rates map[TaxJurisdiction28]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine28() *TaxCalculatorEngine28 {
	return &TaxCalculatorEngine28{
		rates: map[TaxJurisdiction28]float64{
			JurisdictionUS28:   0.0825,
			JurisdictionEU28:   0.2000,
			JurisdictionAPAC28: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine28) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction28, amount float64) (*TaxAssessment28, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment28{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
