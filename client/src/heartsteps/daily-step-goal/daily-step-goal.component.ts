import { Component, Input, OnDestroy } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

@Component({
    selector: 'heartsteps-daily-step-goal',
    templateUrl: './daily-step-goal.html'
})
export class DailyStepGoalComponent {
    public dailyStepGoal: number = 8000;
    public dailyStepDiff: number = 7;

    constructor(
        private heartstepsServer: HeartstepsServer
    ){
        this.update();
    }

    private update() {
        this.heartstepsServer.get('dailystepgoals')
        .then((data) => {
            console.log(data);
            console.log('Got a response from the server');

            this.dailyStepGoal = data[data.length - 1]["step_goal"];
        })
        .catch(() => {
            console.log('Daily step count goal failed')
        })
    }
}

