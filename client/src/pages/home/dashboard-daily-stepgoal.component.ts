import { Component } from "@angular/core";
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

@Component({
    selector: "dashboard-daily-stepgoal",
    templateUrl: "./dashboard-daily-stepgoal.component.html",
})
export class DashboardDailyStepgoalComponent {
//     public dailyStepGoal: number = 10000;
//     constructor(
//         private heartstepsServer: HeartstepsServer
//     ) {
//         this.update();
//     }
//
//     private update() {
//
//     }
    public dailyStepGoal: number = 0;
    public dailyStepsToGo: number = 0;
    public dailyStep: number = 0;

    constructor(
        private heartstepsServer: HeartstepsServer,
    ){
        this.update();
    }

    private update() {
        console.log("trying to update daily step goal (old)");
        this.heartstepsServer.get('todaystepgoal')
        .then((data) => {
            console.log("DailyStepGoalComponent.update()", data);
            console.log('GET LATEST GOAL: Got a response from the server');

            this.dailyStepGoal = data["step_goal"];
            this.dailyStep = data["steps"];
            this.dailyStepsToGo = this.dailyStepGoal - this.dailyStep;
            if (this.dailyStepsToGo < 0) {
                this.dailyStepsToGo = 0;
            }
        })
        .catch(() => {
            console.log('Daily step count goal failed')
        })
}
}
