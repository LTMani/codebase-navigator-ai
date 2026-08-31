package taxengine36

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction36 string

const (
	JurisdictionUS36 TaxJurisdiction36 = "US_FEDERAL"
	JurisdictionEU36 TaxJurisdiction36 = "EU_VAT"
	JurisdictionAPAC36 TaxJurisdiction36 = "APAC_GST"
)

type TaxAssessment36 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction36  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine36 struct {
	rates map[TaxJurisdiction36]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine36() *TaxCalculatorEngine36 {
	return &TaxCalculatorEngine36{
		rates: map[TaxJurisdiction36]float64{
			JurisdictionUS36:   0.0825,
			JurisdictionEU36:   0.2000,
			JurisdictionAPAC36: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine36) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction36, amount float64) (*TaxAssessment36, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment36{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
