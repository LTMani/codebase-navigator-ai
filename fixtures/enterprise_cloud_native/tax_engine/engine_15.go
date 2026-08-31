package taxengine15

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction15 string

const (
	JurisdictionUS15 TaxJurisdiction15 = "US_FEDERAL"
	JurisdictionEU15 TaxJurisdiction15 = "EU_VAT"
	JurisdictionAPAC15 TaxJurisdiction15 = "APAC_GST"
)

type TaxAssessment15 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction15  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine15 struct {
	rates map[TaxJurisdiction15]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine15() *TaxCalculatorEngine15 {
	return &TaxCalculatorEngine15{
		rates: map[TaxJurisdiction15]float64{
			JurisdictionUS15:   0.0825,
			JurisdictionEU15:   0.2000,
			JurisdictionAPAC15: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine15) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction15, amount float64) (*TaxAssessment15, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment15{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
