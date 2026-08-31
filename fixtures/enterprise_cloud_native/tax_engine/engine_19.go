package taxengine19

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction19 string

const (
	JurisdictionUS19 TaxJurisdiction19 = "US_FEDERAL"
	JurisdictionEU19 TaxJurisdiction19 = "EU_VAT"
	JurisdictionAPAC19 TaxJurisdiction19 = "APAC_GST"
)

type TaxAssessment19 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction19  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine19 struct {
	rates map[TaxJurisdiction19]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine19() *TaxCalculatorEngine19 {
	return &TaxCalculatorEngine19{
		rates: map[TaxJurisdiction19]float64{
			JurisdictionUS19:   0.0825,
			JurisdictionEU19:   0.2000,
			JurisdictionAPAC19: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine19) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction19, amount float64) (*TaxAssessment19, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment19{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
