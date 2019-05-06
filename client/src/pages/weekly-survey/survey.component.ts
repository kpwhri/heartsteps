import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { ActivatedRoute } from "@angular/router";
import { WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { LoadingService } from "@infrastructure/loading.service";

@Component({
    templateUrl: './survey.component.html'
})
export class SurveyComponent implements OnInit {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;
    public questions: Array<any>;

    public week: Week;

    constructor(
        private activatedRoute: ActivatedRoute,
        private weekService: WeekService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.form = new FormGroup({});

        const weeklySurvey:WeeklySurvey = this.activatedRoute.snapshot.data['weeklySurvey'];
        this.week = weeklySurvey.currentWeek;

        this.loadingService.show('Loading survey');
        this.weekService.getWeekSurvey(this.week)
        .then((survey) => {
            this.loadingService.dismiss();
            console.log(survey);
            const questions = [];
            survey.questions.forEach((question: any) => {
                this.form.addControl(question.name, new FormControl());
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
        })
    }

    nextPage() {
        this.loadingService.show('Saving survey');
        this.weekService.submitWeekSurvey(this.week, this.form.value)
        .then(() => {
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
