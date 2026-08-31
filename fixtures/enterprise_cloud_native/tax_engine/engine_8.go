package taxengine8

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction8 string

const (
	JurisdictionUS8 TaxJurisdiction8 = "US_FEDERAL"
	JurisdictionEU8 TaxJurisdiction8 = "EU_VAT"
	JurisdictionAPAC8 TaxJurisdiction8 = "APAC_GST"
)

type TaxAssessment8 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction8  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine8 struct {
	rates map[TaxJurisdiction8]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine8() *TaxCalculatorEngine8 {
	return &TaxCalculatorEngine8{
		rates: map[TaxJurisdiction8]float64{
			JurisdictionUS8:   0.0825,
			JurisdictionEU8:   0.2000,
			JurisdictionAPAC8: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine8) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction8, amount float64) (*TaxAssessment8, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment8{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
