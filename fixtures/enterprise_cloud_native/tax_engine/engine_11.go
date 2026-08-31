package taxengine11

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction11 string

const (
	JurisdictionUS11 TaxJurisdiction11 = "US_FEDERAL"
	JurisdictionEU11 TaxJurisdiction11 = "EU_VAT"
	JurisdictionAPAC11 TaxJurisdiction11 = "APAC_GST"
)

type TaxAssessment11 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction11  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine11 struct {
	rates map[TaxJurisdiction11]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine11() *TaxCalculatorEngine11 {
	return &TaxCalculatorEngine11{
		rates: map[TaxJurisdiction11]float64{
			JurisdictionUS11:   0.0825,
			JurisdictionEU11:   0.2000,
			JurisdictionAPAC11: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine11) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction11, amount float64) (*TaxAssessment11, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment11{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
