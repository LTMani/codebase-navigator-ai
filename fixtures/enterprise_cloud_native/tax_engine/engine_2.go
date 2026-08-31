package taxengine2

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction2 string

const (
	JurisdictionUS2 TaxJurisdiction2 = "US_FEDERAL"
	JurisdictionEU2 TaxJurisdiction2 = "EU_VAT"
	JurisdictionAPAC2 TaxJurisdiction2 = "APAC_GST"
)

type TaxAssessment2 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction2  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine2 struct {
	rates map[TaxJurisdiction2]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine2() *TaxCalculatorEngine2 {
	return &TaxCalculatorEngine2{
		rates: map[TaxJurisdiction2]float64{
			JurisdictionUS2:   0.0825,
			JurisdictionEU2:   0.2000,
			JurisdictionAPAC2: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine2) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction2, amount float64) (*TaxAssessment2, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment2{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
