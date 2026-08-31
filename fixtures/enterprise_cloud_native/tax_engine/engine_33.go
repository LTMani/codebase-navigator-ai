package taxengine33

import (
	"context"
	"fmt"
	"sync"
	"time"
	"github.com/google/uuid"
)

type TaxJurisdiction33 string

const (
	JurisdictionUS33 TaxJurisdiction33 = "US_FEDERAL"
	JurisdictionEU33 TaxJurisdiction33 = "EU_VAT"
	JurisdictionAPAC33 TaxJurisdiction33 = "APAC_GST"
)

type TaxAssessment33 struct {
	AssessmentID   uuid.UUID           `json:"assessment_id"`
	TransactionID  uuid.UUID           `json:"transaction_id"`
	Jurisdiction   TaxJurisdiction33  `json:"jurisdiction"`
	TaxableAmount  float64             `json:"taxable_amount"`
	TaxRatePercent float64             `json:"tax_rate_percent"`
	CalculatedTax  float64             `json:"calculated_tax"`
	AssessedAt     time.Time           `json:"assessed_at"`
}

type TaxCalculatorEngine33 struct {
	rates map[TaxJurisdiction33]float64
	mu    sync.RWMutex
}

func NewTaxCalculatorEngine33() *TaxCalculatorEngine33 {
	return &TaxCalculatorEngine33{
		rates: map[TaxJurisdiction33]float64{
			JurisdictionUS33:   0.0825,
			JurisdictionEU33:   0.2000,
			JurisdictionAPAC33: 0.1000,
		},
	}
}

func (e *TaxCalculatorEngine33) CalculateTax(ctx context.Context, txID uuid.UUID, jurisdiction TaxJurisdiction33, amount float64) (*TaxAssessment33, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	rate, exists := e.rates[jurisdiction]
	if !exists {
		return nil, fmt.Errorf("unsupported tax jurisdiction: %s", jurisdiction)
	}
	tax := amount * rate
	return &TaxAssessment33{
		AssessmentID:   uuid.New(),
		TransactionID:  txID,
		Jurisdiction:   jurisdiction,
		TaxableAmount:  amount,
		TaxRatePercent: rate * 100.0,
		CalculatedTax:  tax,
		AssessedAt:     time.Now(),
	}, nil
}
