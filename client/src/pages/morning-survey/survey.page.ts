import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { ActivatedRoute } from "@angular/router";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './survey.page.html'
})
export class SurveyPageComponent implements OnInit {
    public form: FormGroup;
    public error: string;
    public questions: Array<any>;

    public moodChoices: Array<SelectOption> = [{
        name: 'Alert',
        value: 'alert'
    }, {
        name: 'Fatigued',
        value: 'fatigued'
    }, {
        name: 'Tense',
        value: 'tense'
    }, {
        name: 'Calm',
        value: 'calm'
    }];
    
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private activatedRoute: ActivatedRoute,
        private morningMessageService: MorningMessageService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        const morningMessage: MorningMessage = this.activatedRoute.snapshot.data['morningMessage'];

        this.form = new FormGroup({
            mood: new FormControl()
        });

        if(morningMessage.survey.questions) {
            const questions = [];
            morningMessage.survey.questions.forEach((question) => {
                questions.push({
                    name: question.name,
                    label: question.label,
                    options: question.options.map((option:any) => {
                        return {
                            name: option.label,
                            value: option.value
                        };
                    })
                });
                this.form.addControl(question.name, new FormControl());
            });
            this.questions = questions;
        }

    }

    public done() {
        this.loadingService.show('Saving survey');
        const values = Object.assign({}, this.form.value);
        delete values['mood'];
        this.morningMessageService.submitSurvey(values)
        .then(() => {
            this.next.emit();
        })
        .catch((error) => {
            console.log(error);
            this.error = 'There was an error'
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
