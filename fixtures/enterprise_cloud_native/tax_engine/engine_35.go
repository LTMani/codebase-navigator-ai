package taxengine35

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction35 string

const (
	JurisdictionUS35 TaxJurisdiction35 = "US_FEDERAL"
	JurisdictionEU35 TaxJurisdiction35 = "EU_VAT"
	JurisdictionAPAC35 TaxJurisdiction35 = "APAC_GST"
)

type TaxAssessment35 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction35  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine35 struct {
	rates map[TaxJurisdiction35]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine35() *TaxCalculatorEngine35 {
	return &TaxCalculatorEngine35{
		rates: map[TaxJurisdiction35]float64{
			JurisdictionUS35:   0.0825,
			JurisdictionEU35:   0.2000,
			JurisdictionAPAC35: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine35) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction35, amount float64) (*TaxAssessment35, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment35{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
