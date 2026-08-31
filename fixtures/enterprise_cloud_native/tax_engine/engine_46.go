package taxengine46

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction46 string

const (
	JurisdictionUS46 TaxJurisdiction46 = "US_FEDERAL"
	JurisdictionEU46 TaxJurisdiction46 = "EU_VAT"
	JurisdictionAPAC46 TaxJurisdiction46 = "APAC_GST"
)

type TaxAssessment46 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction46  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine46 struct {
	rates map[TaxJurisdiction46]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine46() *TaxCalculatorEngine46 {
	return &TaxCalculatorEngine46{
		rates: map[TaxJurisdiction46]float64{
			JurisdictionUS46:   0.0825,
			JurisdictionEU46:   0.2000,
			JurisdictionAPAC46: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine46) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction46, amount float64) (*TaxAssessment46, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment46{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
