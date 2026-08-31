package taxengine1

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction1 string

const (
	JurisdictionUS1 TaxJurisdiction1 = "US_FEDERAL"
	JurisdictionEU1 TaxJurisdiction1 = "EU_VAT"
	JurisdictionAPAC1 TaxJurisdiction1 = "APAC_GST"
)

type TaxAssessment1 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction1  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine1 struct {
	rates map[TaxJurisdiction1]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine1() *TaxCalculatorEngine1 {
	return &TaxCalculatorEngine1{
		rates: map[TaxJurisdiction1]float64{
			JurisdictionUS1:   0.0825,
			JurisdictionEU1:   0.2000,
			JurisdictionAPAC1: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine1) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction1, amount float64) (*TaxAssessment1, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment1{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
