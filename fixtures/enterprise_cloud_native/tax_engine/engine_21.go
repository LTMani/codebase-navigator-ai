package taxengine21

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction21 string

const (
	JurisdictionUS21 TaxJurisdiction21 = "US_FEDERAL"
	JurisdictionEU21 TaxJurisdiction21 = "EU_VAT"
	JurisdictionAPAC21 TaxJurisdiction21 = "APAC_GST"
)

type TaxAssessment21 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction21  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine21 struct {
	rates map[TaxJurisdiction21]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine21() *TaxCalculatorEngine21 {
	return &TaxCalculatorEngine21{
		rates: map[TaxJurisdiction21]float64{
			JurisdictionUS21:   0.0825,
			JurisdictionEU21:   0.2000,
			JurisdictionAPAC21: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine21) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction21, amount float64) (*TaxAssessment21, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment21{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
