package taxengine45

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction45 string

const (
	JurisdictionUS45 TaxJurisdiction45 = "US_FEDERAL"
	JurisdictionEU45 TaxJurisdiction45 = "EU_VAT"
	JurisdictionAPAC45 TaxJurisdiction45 = "APAC_GST"
)

type TaxAssessment45 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction45  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine45 struct {
	rates map[TaxJurisdiction45]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine45() *TaxCalculatorEngine45 {
	return &TaxCalculatorEngine45{
		rates: map[TaxJurisdiction45]float64{
			JurisdictionUS45:   0.0825,
			JurisdictionEU45:   0.2000,
			JurisdictionAPAC45: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine45) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction45, amount float64) (*TaxAssessment45, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment45{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
