package taxengine22

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction22 string

const (
	JurisdictionUS22 TaxJurisdiction22 = "US_FEDERAL"
	JurisdictionEU22 TaxJurisdiction22 = "EU_VAT"
	JurisdictionAPAC22 TaxJurisdiction22 = "APAC_GST"
)

type TaxAssessment22 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction22  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine22 struct {
	rates map[TaxJurisdiction22]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine22() *TaxCalculatorEngine22 {
	return &TaxCalculatorEngine22{
		rates: map[TaxJurisdiction22]float64{
			JurisdictionUS22:   0.0825,
			JurisdictionEU22:   0.2000,
			JurisdictionAPAC22: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine22) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction22, amount float64) (*TaxAssessment22, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment22{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
