package taxengine10

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction10 string

const (
	JurisdictionUS10 TaxJurisdiction10 = "US_FEDERAL"
	JurisdictionEU10 TaxJurisdiction10 = "EU_VAT"
	JurisdictionAPAC10 TaxJurisdiction10 = "APAC_GST"
)

type TaxAssessment10 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction10  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine10 struct {
	rates map[TaxJurisdiction10]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine10() *TaxCalculatorEngine10 {
	return &TaxCalculatorEngine10{
		rates: map[TaxJurisdiction10]float64{
			JurisdictionUS10:   0.0825,
			JurisdictionEU10:   0.2000,
			JurisdictionAPAC10: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine10) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction10, amount float64) (*TaxAssessment10, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment10{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
