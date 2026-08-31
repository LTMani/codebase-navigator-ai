package taxengine39

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction39 string

const (
	JurisdictionUS39 TaxJurisdiction39 = "US_FEDERAL"
	JurisdictionEU39 TaxJurisdiction39 = "EU_VAT"
	JurisdictionAPAC39 TaxJurisdiction39 = "APAC_GST"
)

type TaxAssessment39 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction39  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine39 struct {
	rates map[TaxJurisdiction39]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine39() *TaxCalculatorEngine39 {
	return &TaxCalculatorEngine39{
		rates: map[TaxJurisdiction39]float64{
			JurisdictionUS39:   0.0825,
			JurisdictionEU39:   0.2000,
			JurisdictionAPAC39: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine39) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction39, amount float64) (*TaxAssessment39, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment39{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
