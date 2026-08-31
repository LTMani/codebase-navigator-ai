package taxengine18

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction18 string

const (
	JurisdictionUS18 TaxJurisdiction18 = "US_FEDERAL"
	JurisdictionEU18 TaxJurisdiction18 = "EU_VAT"
	JurisdictionAPAC18 TaxJurisdiction18 = "APAC_GST"
)

type TaxAssessment18 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction18  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine18 struct {
	rates map[TaxJurisdiction18]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine18() *TaxCalculatorEngine18 {
	return &TaxCalculatorEngine18{
		rates: map[TaxJurisdiction18]float64{
			JurisdictionUS18:   0.0825,
			JurisdictionEU18:   0.2000,
			JurisdictionAPAC18: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine18) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction18, amount float64) (*TaxAssessment18, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment18{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
