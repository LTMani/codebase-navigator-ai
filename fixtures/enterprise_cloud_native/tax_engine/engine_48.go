package taxengine48

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction48 string

const (
	JurisdictionUS48 TaxJurisdiction48 = "US_FEDERAL"
	JurisdictionEU48 TaxJurisdiction48 = "EU_VAT"
	JurisdictionAPAC48 TaxJurisdiction48 = "APAC_GST"
)

type TaxAssessment48 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction48  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine48 struct {
	rates map[TaxJurisdiction48]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine48() *TaxCalculatorEngine48 {
	return &TaxCalculatorEngine48{
		rates: map[TaxJurisdiction48]float64{
			JurisdictionUS48:   0.0825,
			JurisdictionEU48:   0.2000,
			JurisdictionAPAC48: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine48) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction48, amount float64) (*TaxAssessment48, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment48{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
