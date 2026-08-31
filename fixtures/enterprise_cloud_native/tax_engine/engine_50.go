package taxengine50

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction50 string

const (
	JurisdictionUS50 TaxJurisdiction50 = "US_FEDERAL"
	JurisdictionEU50 TaxJurisdiction50 = "EU_VAT"
	JurisdictionAPAC50 TaxJurisdiction50 = "APAC_GST"
)

type TaxAssessment50 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction50  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine50 struct {
	rates map[TaxJurisdiction50]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine50() *TaxCalculatorEngine50 {
	return &TaxCalculatorEngine50{
		rates: map[TaxJurisdiction50]float64{
			JurisdictionUS50:   0.0825,
			JurisdictionEU50:   0.2000,
			JurisdictionAPAC50: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine50) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction50, amount float64) (*TaxAssessment50, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment50{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
