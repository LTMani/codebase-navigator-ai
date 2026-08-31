// Enterprise State Slice & Metric Store 36
export interface TelemetryEventPayload36 {
  id: string;
  serviceName: string;
  durationMs: number;
  isSuccess: boolean;
  timestamp: string;
}

export class TelemetryStateStore36 {
  private events: TelemetryEventPayload36[] = [];

  public recordEvent(event: TelemetryEventPayload36): void {
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
