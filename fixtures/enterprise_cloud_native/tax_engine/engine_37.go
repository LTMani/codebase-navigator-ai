package taxengine37

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction37 string

const (
	JurisdictionUS37 TaxJurisdiction37 = "US_FEDERAL"
	JurisdictionEU37 TaxJurisdiction37 = "EU_VAT"
	JurisdictionAPAC37 TaxJurisdiction37 = "APAC_GST"
)

type TaxAssessment37 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction37  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine37 struct {
	rates map[TaxJurisdiction37]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine37() *TaxCalculatorEngine37 {
	return &TaxCalculatorEngine37{
		rates: map[TaxJurisdiction37]float64{
			JurisdictionUS37:   0.0825,
			JurisdictionEU37:   0.2000,
			JurisdictionAPAC37: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine37) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction37, amount float64) (*TaxAssessment37, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment37{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
