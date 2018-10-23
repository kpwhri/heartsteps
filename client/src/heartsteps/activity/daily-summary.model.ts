import * as moment from 'moment';

export class DailySummary {

    public moderateMinutes: number = 0;
    public vigorousMinutes: number = 0;
    public totalMinutes: number;

    public totalSteps: number = 0;
    public totalMiles: number = 0;

    constructor(
        moderateMinutes: number,
        vigorousMinutes: number,
        totalSteps: number,
        totalMiles: number
    ){
        this.moderateMinutes = moderateMinutes;
        this.vigorousMinutes = vigorousMinutes;
        this.totalMinutes = moderateMinutes + vigorousMinutes;

        this.totalSteps = totalSteps;
        this.totalMiles = totalMiles;
    }
}