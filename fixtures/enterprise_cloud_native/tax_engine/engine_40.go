package taxengine40

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction40 string

const (
	JurisdictionUS40 TaxJurisdiction40 = "US_FEDERAL"
	JurisdictionEU40 TaxJurisdiction40 = "EU_VAT"
	JurisdictionAPAC40 TaxJurisdiction40 = "APAC_GST"
)

type TaxAssessment40 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction40  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine40 struct {
	rates map[TaxJurisdiction40]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine40() *TaxCalculatorEngine40 {
	return &TaxCalculatorEngine40{
		rates: map[TaxJurisdiction40]float64{
			JurisdictionUS40:   0.0825,
			JurisdictionEU40:   0.2000,
			JurisdictionAPAC40: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine40) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction40, amount float64) (*TaxAssessment40, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment40{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
