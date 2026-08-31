package taxengine24

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction24 string

const (
	JurisdictionUS24 TaxJurisdiction24 = "US_FEDERAL"
	JurisdictionEU24 TaxJurisdiction24 = "EU_VAT"
	JurisdictionAPAC24 TaxJurisdiction24 = "APAC_GST"
)

type TaxAssessment24 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction24  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine24 struct {
	rates map[TaxJurisdiction24]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine24() *TaxCalculatorEngine24 {
	return &TaxCalculatorEngine24{
		rates: map[TaxJurisdiction24]float64{
			JurisdictionUS24:   0.0825,
			JurisdictionEU24:   0.2000,
			JurisdictionAPAC24: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine24) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction24, amount float64) (*TaxAssessment24, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment24{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
