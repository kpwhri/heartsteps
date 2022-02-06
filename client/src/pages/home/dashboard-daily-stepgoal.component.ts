import { Component } from "@angular/core";
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

@Component({
    selector: "dashboard-daily-stepgoal",
    templateUrl: "./dashboard-daily-stepgoal.component.html",
})
export class DashboardDailyStepgoalComponent {
    public dailyStepGoal: number = 10000;
    constructor(
        private heartstepsServer: HeartstepsServer
    ) {
        this.update();
    }

    private update() {
        
    }
}
