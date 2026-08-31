package taxengine38

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction38 string

const (
	JurisdictionUS38 TaxJurisdiction38 = "US_FEDERAL"
	JurisdictionEU38 TaxJurisdiction38 = "EU_VAT"
	JurisdictionAPAC38 TaxJurisdiction38 = "APAC_GST"
)

type TaxAssessment38 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction38  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine38 struct {
	rates map[TaxJurisdiction38]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine38() *TaxCalculatorEngine38 {
	return &TaxCalculatorEngine38{
		rates: map[TaxJurisdiction38]float64{
			JurisdictionUS38:   0.0825,
			JurisdictionEU38:   0.2000,
			JurisdictionAPAC38: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine38) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction38, amount float64) (*TaxAssessment38, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment38{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
