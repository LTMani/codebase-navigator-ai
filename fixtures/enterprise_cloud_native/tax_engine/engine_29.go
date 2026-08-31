package taxengine29

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction29 string

const (
	JurisdictionUS29 TaxJurisdiction29 = "US_FEDERAL"
	JurisdictionEU29 TaxJurisdiction29 = "EU_VAT"
	JurisdictionAPAC29 TaxJurisdiction29 = "APAC_GST"
)

type TaxAssessment29 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction29  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine29 struct {
	rates map[TaxJurisdiction29]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine29() *TaxCalculatorEngine29 {
	return &TaxCalculatorEngine29{
		rates: map[TaxJurisdiction29]float64{
			JurisdictionUS29:   0.0825,
			JurisdictionEU29:   0.2000,
			JurisdictionAPAC29: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine29) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction29, amount float64) (*TaxAssessment29, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment29{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
