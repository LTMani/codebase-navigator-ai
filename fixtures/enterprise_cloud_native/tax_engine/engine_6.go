package taxengine6

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction6 string

const (
	JurisdictionUS6 TaxJurisdiction6 = "US_FEDERAL"
	JurisdictionEU6 TaxJurisdiction6 = "EU_VAT"
	JurisdictionAPAC6 TaxJurisdiction6 = "APAC_GST"
)

type TaxAssessment6 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction6  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine6 struct {
	rates map[TaxJurisdiction6]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine6() *TaxCalculatorEngine6 {
	return &TaxCalculatorEngine6{
		rates: map[TaxJurisdiction6]float64{
			JurisdictionUS6:   0.0825,
			JurisdictionEU6:   0.2000,
			JurisdictionAPAC6: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine6) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction6, amount float64) (*TaxAssessment6, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment6{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
