import { Component } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

@Component({
    selector: 'heartsteps-daily-step-goal',
    templateUrl: './daily-step-goal.html'
})
export class DailyStepGoalComponent {
    public dailyStepGoal: number = 0;
    public dailyStepsToGo: number = 0;
    public dailyStep: number = 0;
    
    constructor(
        private heartstepsServer: HeartstepsServer,
//         private dailySummary: DailySummaryComponent
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

    // The following function is used to test if the new method of calculation by multiplying the median of the last 5
    // step counts by a defined multiplier is correctly implemented.
//     private testUpdate() {
//         console.log("trying to update daily step goal (new)");
//         this.heartstepsServer.get('newmultipliergoal')
//         .then((data) => {
//             console.log(data);
//             console.log('GET LATEST MULTI GOAL: Got a response from the server');
//
//             //this.dailyStepGoal = data[0]["goal"];
//
//             var step_median = (data[4]["steps"] + data[5]["steps"])/2;
// //             this.dailyStepGoal = Math.round(step_median)*data[0]["multiplier"];
//             this.dailyStepGoal = Math.round(step_median);
//         })
//         .catch(() => {
//             console.log('Daily step count goal failed')
//         })
//     }

//     private updateAll() {
//         this.heartstepsServer.get('newgoal')
//         .then((data) => {
//             console.log(data);
//             console.log('NEW GOAL: Got a response from the server');
//
//             var step_median = (data[4]["steps"] + data[5]["steps"])/2;
//             this.dailyStepGoal = Math.round(step_median);
//
//             console.log("NEW STEP GOAL: " + this.dailyStepGoal);
//             console.log("CURRENT STEPS: " + this.dailySummary.steps);
//
//             this.dailyStepDiff = this.dailyStepGoal - this.dailySummary.steps;
//         })
//         .catch(() => {
//             console.log('New goal failed');
//         })
//     }
}

