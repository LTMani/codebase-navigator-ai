// Enterprise State Slice & Metric Store 31
export interface TelemetryEventPayload31 {
  id: string;
  serviceName: string;
  durationMs: number;
  isSuccess: boolean;
  timestamp: string;
}

export class TelemetryStateStore31 {
  private events: TelemetryEventPayload31[] = [];

  public recordEvent(event: TelemetryEventPayload31): void {
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
