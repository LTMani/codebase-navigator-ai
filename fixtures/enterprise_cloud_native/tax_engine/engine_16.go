package taxengine16

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction16 string

const (
	JurisdictionUS16 TaxJurisdiction16 = "US_FEDERAL"
	JurisdictionEU16 TaxJurisdiction16 = "EU_VAT"
	JurisdictionAPAC16 TaxJurisdiction16 = "APAC_GST"
)

type TaxAssessment16 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction16  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine16 struct {
	rates map[TaxJurisdiction16]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine16() *TaxCalculatorEngine16 {
	return &TaxCalculatorEngine16{
		rates: map[TaxJurisdiction16]float64{
			JurisdictionUS16:   0.0825,
			JurisdictionEU16:   0.2000,
			JurisdictionAPAC16: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine16) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction16, amount float64) (*TaxAssessment16, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment16{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
