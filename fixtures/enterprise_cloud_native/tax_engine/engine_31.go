package taxengine31

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction31 string

const (
	JurisdictionUS31 TaxJurisdiction31 = "US_FEDERAL"
	JurisdictionEU31 TaxJurisdiction31 = "EU_VAT"
	JurisdictionAPAC31 TaxJurisdiction31 = "APAC_GST"
)

type TaxAssessment31 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction31  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine31 struct {
	rates map[TaxJurisdiction31]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine31() *TaxCalculatorEngine31 {
	return &TaxCalculatorEngine31{
		rates: map[TaxJurisdiction31]float64{
			JurisdictionUS31:   0.0825,
			JurisdictionEU31:   0.2000,
			JurisdictionAPAC31: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine31) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction31, amount float64) (*TaxAssessment31, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment31{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
