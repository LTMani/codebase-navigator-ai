package taxengine47

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction47 string

const (
	JurisdictionUS47 TaxJurisdiction47 = "US_FEDERAL"
	JurisdictionEU47 TaxJurisdiction47 = "EU_VAT"
	JurisdictionAPAC47 TaxJurisdiction47 = "APAC_GST"
)

type TaxAssessment47 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction47  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine47 struct {
	rates map[TaxJurisdiction47]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine47() *TaxCalculatorEngine47 {
	return &TaxCalculatorEngine47{
		rates: map[TaxJurisdiction47]float64{
			JurisdictionUS47:   0.0825,
			JurisdictionEU47:   0.2000,
			JurisdictionAPAC47: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine47) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction47, amount float64) (*TaxAssessment47, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment47{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
