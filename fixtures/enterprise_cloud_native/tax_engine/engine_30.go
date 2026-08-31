package taxengine30

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction30 string

const (
	JurisdictionUS30 TaxJurisdiction30 = "US_FEDERAL"
	JurisdictionEU30 TaxJurisdiction30 = "EU_VAT"
	JurisdictionAPAC30 TaxJurisdiction30 = "APAC_GST"
)

type TaxAssessment30 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction30  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine30 struct {
	rates map[TaxJurisdiction30]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine30() *TaxCalculatorEngine30 {
	return &TaxCalculatorEngine30{
		rates: map[TaxJurisdiction30]float64{
			JurisdictionUS30:   0.0825,
			JurisdictionEU30:   0.2000,
			JurisdictionAPAC30: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine30) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction30, amount float64) (*TaxAssessment30, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment30{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
