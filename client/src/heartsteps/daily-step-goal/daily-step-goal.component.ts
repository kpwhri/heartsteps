import { Component, Input, OnDestroy } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { DailySummaryComponent } from '@heartsteps/daily-summaries/daily-summary.component';

@Component({
    selector: 'heartsteps-daily-step-goal',
    templateUrl: './daily-step-goal.html'
})
export class DailyStepGoalComponent {
    public dailyStepGoal: number = 8000;
    public dailyStepDiff: number = 8000;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private dailySummary: DailySummaryComponent
    ){
        this.updateAll();
    }

    private update() {
        this.heartstepsServer.get('dailystepgoals')
        .then((data) => {
            console.log(data);
            console.log('GET LATEST GOAL: Got a response from the server');

            this.dailyStepGoal = data[data.length - 1]["step_goal"];
        })
        .catch(() => {
            console.log('Daily step count goal failed')
        })
    }

    private updateAll() {
        this.heartstepsServer.get('newgoal')
        .then((data) => {
            console.log(data);
            console.log('NEW GOAL: Got a response from the server');

            var step_median = (data[4]["steps"] + data[5]["steps"])/2;
            this.dailyStepGoal = Math.round(step_median);

            console.log("NEW STEP GOAL: " + this.dailyStepGoal);
            console.log("CURRENT STEPS: " + this.dailySummary.steps);

            this.dailyStepDiff = this.dailyStepGoal - this.dailySummary.steps;
        })
        .catch(() => {
            console.log('New goal failed');
        })
    }
}

