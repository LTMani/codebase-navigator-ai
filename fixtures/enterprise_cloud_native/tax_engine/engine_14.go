package taxengine14

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction14 string

const (
	JurisdictionUS14 TaxJurisdiction14 = "US_FEDERAL"
	JurisdictionEU14 TaxJurisdiction14 = "EU_VAT"
	JurisdictionAPAC14 TaxJurisdiction14 = "APAC_GST"
)

type TaxAssessment14 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction14  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine14 struct {
	rates map[TaxJurisdiction14]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine14() *TaxCalculatorEngine14 {
	return &TaxCalculatorEngine14{
		rates: map[TaxJurisdiction14]float64{
			JurisdictionUS14:   0.0825,
			JurisdictionEU14:   0.2000,
			JurisdictionAPAC14: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine14) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction14, amount float64) (*TaxAssessment14, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment14{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
