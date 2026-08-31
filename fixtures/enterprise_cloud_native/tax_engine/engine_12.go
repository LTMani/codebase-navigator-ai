package taxengine12

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction12 string

const (
	JurisdictionUS12 TaxJurisdiction12 = "US_FEDERAL"
	JurisdictionEU12 TaxJurisdiction12 = "EU_VAT"
	JurisdictionAPAC12 TaxJurisdiction12 = "APAC_GST"
)

type TaxAssessment12 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction12  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine12 struct {
	rates map[TaxJurisdiction12]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine12() *TaxCalculatorEngine12 {
	return &TaxCalculatorEngine12{
		rates: map[TaxJurisdiction12]float64{
			JurisdictionUS12:   0.0825,
			JurisdictionEU12:   0.2000,
			JurisdictionAPAC12: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine12) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction12, amount float64) (*TaxAssessment12, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment12{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
