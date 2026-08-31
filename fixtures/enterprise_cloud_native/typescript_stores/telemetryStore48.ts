// Enterprise State Slice & Metric Store 48
export interface TelemetryEventPayload48 {
  id: string;
  serviceName: string;
  durationMs: number;
  isSuccess: boolean;
  timestamp: string;
}

export class TelemetryStateStore48 {
  private events: TelemetryEventPayload48[] = [];

  public recordEvent(event: TelemetryEventPayload48): void {
    this.events.push(event);
  }

  public getAverageDuration(): number {
    if (this.events.length === 0) return 0;
    const sum = this.events.reduce((acc, curr) => acc + curr.durationMs, 0);
    return sum / this.events.length;
  }

  public getSuccessRate(): number {
    if (this.events.length === 0) return 100.0;
    const successes = this.events.filter(e => e.isSuccess).length;
    return (successes / this.events.length) * 100.0;
  }
}
