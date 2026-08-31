package taxengine17

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction17 string

const (
	JurisdictionUS17 TaxJurisdiction17 = "US_FEDERAL"
	JurisdictionEU17 TaxJurisdiction17 = "EU_VAT"
	JurisdictionAPAC17 TaxJurisdiction17 = "APAC_GST"
)

type TaxAssessment17 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction17  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine17 struct {
	rates map[TaxJurisdiction17]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine17() *TaxCalculatorEngine17 {
	return &TaxCalculatorEngine17{
		rates: map[TaxJurisdiction17]float64{
			JurisdictionUS17:   0.0825,
			JurisdictionEU17:   0.2000,
			JurisdictionAPAC17: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine17) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction17, amount float64) (*TaxAssessment17, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment17{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
