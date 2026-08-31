package taxengine27

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction27 string

const (
	JurisdictionUS27 TaxJurisdiction27 = "US_FEDERAL"
	JurisdictionEU27 TaxJurisdiction27 = "EU_VAT"
	JurisdictionAPAC27 TaxJurisdiction27 = "APAC_GST"
)

type TaxAssessment27 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction27  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine27 struct {
	rates map[TaxJurisdiction27]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine27() *TaxCalculatorEngine27 {
	return &TaxCalculatorEngine27{
		rates: map[TaxJurisdiction27]float64{
			JurisdictionUS27:   0.0825,
			JurisdictionEU27:   0.2000,
			JurisdictionAPAC27: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine27) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction27, amount float64) (*TaxAssessment27, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment27{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
