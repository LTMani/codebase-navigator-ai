package taxengine41

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction41 string

const (
	JurisdictionUS41 TaxJurisdiction41 = "US_FEDERAL"
	JurisdictionEU41 TaxJurisdiction41 = "EU_VAT"
	JurisdictionAPAC41 TaxJurisdiction41 = "APAC_GST"
)

type TaxAssessment41 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction41  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine41 struct {
	rates map[TaxJurisdiction41]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine41() *TaxCalculatorEngine41 {
	return &TaxCalculatorEngine41{
		rates: map[TaxJurisdiction41]float64{
			JurisdictionUS41:   0.0825,
			JurisdictionEU41:   0.2000,
			JurisdictionAPAC41: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine41) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction41, amount float64) (*TaxAssessment41, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment41{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
