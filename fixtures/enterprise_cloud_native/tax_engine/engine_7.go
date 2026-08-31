package taxengine7

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction7 string

const (
	JurisdictionUS7 TaxJurisdiction7 = "US_FEDERAL"
	JurisdictionEU7 TaxJurisdiction7 = "EU_VAT"
	JurisdictionAPAC7 TaxJurisdiction7 = "APAC_GST"
)

type TaxAssessment7 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction7  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine7 struct {
	rates map[TaxJurisdiction7]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine7() *TaxCalculatorEngine7 {
	return &TaxCalculatorEngine7{
		rates: map[TaxJurisdiction7]float64{
			JurisdictionUS7:   0.0825,
			JurisdictionEU7:   0.2000,
			JurisdictionAPAC7: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine7) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction7, amount float64) (*TaxAssessment7, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment7{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
