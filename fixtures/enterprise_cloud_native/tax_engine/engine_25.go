package taxengine25

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction25 string

const (
	JurisdictionUS25 TaxJurisdiction25 = "US_FEDERAL"
	JurisdictionEU25 TaxJurisdiction25 = "EU_VAT"
	JurisdictionAPAC25 TaxJurisdiction25 = "APAC_GST"
)

type TaxAssessment25 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction25  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine25 struct {
	rates map[TaxJurisdiction25]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine25() *TaxCalculatorEngine25 {
	return &TaxCalculatorEngine25{
		rates: map[TaxJurisdiction25]float64{
			JurisdictionUS25:   0.0825,
			JurisdictionEU25:   0.2000,
			JurisdictionAPAC25: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine25) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction25, amount float64) (*TaxAssessment25, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment25{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
