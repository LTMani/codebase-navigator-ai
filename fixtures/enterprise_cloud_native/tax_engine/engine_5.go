package taxengine5

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction5 string

const (
	JurisdictionUS5 TaxJurisdiction5 = "US_FEDERAL"
	JurisdictionEU5 TaxJurisdiction5 = "EU_VAT"
	JurisdictionAPAC5 TaxJurisdiction5 = "APAC_GST"
)

type TaxAssessment5 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction5  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine5 struct {
	rates map[TaxJurisdiction5]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine5() *TaxCalculatorEngine5 {
	return &TaxCalculatorEngine5{
		rates: map[TaxJurisdiction5]float64{
			JurisdictionUS5:   0.0825,
			JurisdictionEU5:   0.2000,
			JurisdictionAPAC5: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine5) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction5, amount float64) (*TaxAssessment5, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment5{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
