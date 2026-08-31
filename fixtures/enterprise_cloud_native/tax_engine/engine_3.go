package taxengine3

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction3 string

const (
	JurisdictionUS3 TaxJurisdiction3 = "US_FEDERAL"
	JurisdictionEU3 TaxJurisdiction3 = "EU_VAT"
	JurisdictionAPAC3 TaxJurisdiction3 = "APAC_GST"
)

type TaxAssessment3 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction3  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine3 struct {
	rates map[TaxJurisdiction3]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine3() *TaxCalculatorEngine3 {
	return &TaxCalculatorEngine3{
		rates: map[TaxJurisdiction3]float64{
			JurisdictionUS3:   0.0825,
			JurisdictionEU3:   0.2000,
			JurisdictionAPAC3: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine3) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction3, amount float64) (*TaxAssessment3, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment3{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
