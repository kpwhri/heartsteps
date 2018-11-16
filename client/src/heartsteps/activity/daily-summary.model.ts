export class DailySummary {
    public date: string;
    public updated: Date;

    public moderateMinutes: number = 0;
    public vigorousMinutes: number = 0;
    public totalMinutes: number = 0;

    public totalSteps: number = 0;
    public totalMiles: number = 0;
}