import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { LoadingService } from "@infrastructure/loading.service";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";

@Component({
    templateUrl: './survey.component.html'
})
export class SurveyComponent implements OnInit {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;
    public questions: Array<any>;

    public week: Week;
    private weeklySurvey: WeeklySurvey;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.form = new FormGroup({});

        this.loadingService.show('Loading survey');
        this.weeklySurveyService.get()
        .then((weeklySurvey) => {
            this.weeklySurvey = weeklySurvey;
            this.week = this.weeklySurvey.currentWeek;
            this.update();
        })
        .then(() => {
            this.loadingService.dismiss()
        });
    }

    private update() {
        const questions = [];
        let response = {};
        if(this.weeklySurvey.response) {
            response = this.weeklySurvey.response;
        }
        this.weeklySurvey.questions.forEach((question: any) => {
            this.form.addControl(question.name, new FormControl(response[question.name]));
            questions.push({
                name: question.name,
                label: question.label,
                options: question.options.map((option) => {
                    return {
                        name: option.label,
                        value: option.value
                    }
                })
            });
        });
        this.questions = questions;
    }

    nextPage() {
        this.loadingService.show('Saving survey');
        this.weeklySurveyService.submitSurvey(this.form.value)
        .then(() => {
            this.weeklySurvey.response = this.form.value;
            this.next.emit();
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
