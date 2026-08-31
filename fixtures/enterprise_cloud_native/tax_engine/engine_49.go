package taxengine49

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction49 string

const (
	JurisdictionUS49 TaxJurisdiction49 = "US_FEDERAL"
	JurisdictionEU49 TaxJurisdiction49 = "EU_VAT"
	JurisdictionAPAC49 TaxJurisdiction49 = "APAC_GST"
)

type TaxAssessment49 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction49  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine49 struct {
	rates map[TaxJurisdiction49]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine49() *TaxCalculatorEngine49 {
	return &TaxCalculatorEngine49{
		rates: map[TaxJurisdiction49]float64{
			JurisdictionUS49:   0.0825,
			JurisdictionEU49:   0.2000,
			JurisdictionAPAC49: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine49) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction49, amount float64) (*TaxAssessment49, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment49{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
