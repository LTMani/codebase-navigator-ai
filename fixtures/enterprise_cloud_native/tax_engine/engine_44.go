package taxengine44

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction44 string

const (
	JurisdictionUS44 TaxJurisdiction44 = "US_FEDERAL"
	JurisdictionEU44 TaxJurisdiction44 = "EU_VAT"
	JurisdictionAPAC44 TaxJurisdiction44 = "APAC_GST"
)

type TaxAssessment44 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction44  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine44 struct {
	rates map[TaxJurisdiction44]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine44() *TaxCalculatorEngine44 {
	return &TaxCalculatorEngine44{
		rates: map[TaxJurisdiction44]float64{
			JurisdictionUS44:   0.0825,
			JurisdictionEU44:   0.2000,
			JurisdictionAPAC44: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine44) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction44, amount float64) (*TaxAssessment44, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment44{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
