package taxengine20

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction20 string

const (
	JurisdictionUS20 TaxJurisdiction20 = "US_FEDERAL"
	JurisdictionEU20 TaxJurisdiction20 = "EU_VAT"
	JurisdictionAPAC20 TaxJurisdiction20 = "APAC_GST"
)

type TaxAssessment20 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction20  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine20 struct {
	rates map[TaxJurisdiction20]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine20() *TaxCalculatorEngine20 {
	return &TaxCalculatorEngine20{
		rates: map[TaxJurisdiction20]float64{
			JurisdictionUS20:   0.0825,
			JurisdictionEU20:   0.2000,
			JurisdictionAPAC20: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine20) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction20, amount float64) (*TaxAssessment20, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment20{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
