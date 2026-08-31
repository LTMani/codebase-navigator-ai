package taxengine34

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction34 string

const (
	JurisdictionUS34 TaxJurisdiction34 = "US_FEDERAL"
	JurisdictionEU34 TaxJurisdiction34 = "EU_VAT"
	JurisdictionAPAC34 TaxJurisdiction34 = "APAC_GST"
)

type TaxAssessment34 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction34  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine34 struct {
	rates map[TaxJurisdiction34]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine34() *TaxCalculatorEngine34 {
	return &TaxCalculatorEngine34{
		rates: map[TaxJurisdiction34]float64{
			JurisdictionUS34:   0.0825,
			JurisdictionEU34:   0.2000,
			JurisdictionAPAC34: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine34) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction34, amount float64) (*TaxAssessment34, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment34{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
