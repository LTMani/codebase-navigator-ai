package taxengine26

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction26 string

const (
	JurisdictionUS26 TaxJurisdiction26 = "US_FEDERAL"
	JurisdictionEU26 TaxJurisdiction26 = "EU_VAT"
	JurisdictionAPAC26 TaxJurisdiction26 = "APAC_GST"
)

type TaxAssessment26 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction26  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine26 struct {
	rates map[TaxJurisdiction26]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine26() *TaxCalculatorEngine26 {
	return &TaxCalculatorEngine26{
		rates: map[TaxJurisdiction26]float64{
			JurisdictionUS26:   0.0825,
			JurisdictionEU26:   0.2000,
			JurisdictionAPAC26: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine26) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction26, amount float64) (*TaxAssessment26, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment26{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
