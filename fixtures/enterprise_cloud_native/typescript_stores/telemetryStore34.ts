// Enterprise State Slice & Metric Store 34
export interface TelemetryEventPayload34 {
  id: string;
  serviceName: string;
  durationMs: number;
  isSuccess: boolean;
  timestamp: string;
}

export class TelemetryStateStore34 {
  private events: TelemetryEventPayload34[] = [];

  public recordEvent(event: TelemetryEventPayload34): void {
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
